import abc
import datetime
import json
import asyncio
import logging
import os
import threading
import concurrent.futures
from concurrent.futures import Future
from collections import OrderedDict
from IPython.display import display

from typing import Any, Dict, Optional
from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.base_debugging_helper import BaseDebuggingHelper
from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.common.constants import DEFAULT_DEBUGGING_DIR_PARENT, DEFAULT_DEBUGGING_DIR_TEMPLATE, SYMLINK_DEBUGGING_DIR_PARENT, SYMLINK_DEBUGGING_DIR_TEMPLATE
import sys
import shutil

ADDITIONAL_INSTRUCTION = '''According to the information in this file, provide a root cause analysis, recommendations to fix the issue and the reason behind the recommendation. 
Please select the appropriate solutions to fix the issues. Do not give suggestions that are irrelevant to the root cause. 
When creating a fixed version, first try to modify existing notebook. 
If unable to find the existing notebook or unable to find the cell id in the exiting notebook, create a new notebook file.
Please keep unrelevent cells unchanged, only modify the cells with problems one by one with reasons in the comments. 
If need to suggest to change spark configuration, do that at the start of the notebook and use %%configure -n <connection_name> magic. 
Example useage: 
%%configure -n <connection_name> 
{"conf":
    {"spark.config.key" : "spark.config.value"}
} 
'''

TUNING_SPARK_PROPERTIES = [  
    "spark.executor.cores",
    "spark.executor.memory",
    "spark.executor.instances",
    "spark.driver.memory",
    "spark.driver.cores",
    "spark.default.parallelism", 
    "spark.sql.shuffle.partitions",
    "spark.dynamicAllocation.enabled",
    "spark.memory.fraction",
    "spark.memory.storageFraction",
    "spark.storage.memoryMapThreshold",
    "spark.serializer",
    "spark.shuffle.compress",
    "spark.shuffle.file.buffer",
    "spark.speculation",
    "spark.speculation.interval",
    "spark.speculation.multiplier"
]

GET_SPARK_CONFIGURATIONS = "get_spark_configurations"
GET_SPARK_FAILED_TASKS_DETAILS = "get_spark_failed_task_details"
GET_SPARK_ALL_EXECUTORS = "get_spark_all_executors"
GET_SPARK_FAILED_JOBS = "get_spark_failed_jobs"
GET_SPARK_UNKNOWN_JOBS = "get_spark_unknown_jobs"

CODE_HISTORY_MAX_SIZE = 100000

class SparkDebuggingHelper(BaseDebuggingHelper, metaclass=abc.ABCMeta):
    
    logger = logging.getLogger(__name__)

    
    def __init__(self):
        super().__init__()
        self.spark_ui_base_url = None
        self.code_history = OrderedDict()
        self.request_session = None
        self.session = None
        self._prepare_session_future: Optional[Future] = None
        self.session_stopped = False
        self._prepare_session_lock = threading.Lock()
        
    @abc.abstractmethod
    def prepare_session(self, **kwargs) -> None:
        pass

    
    def prepare_session_in_seperate_thread(self, **kwargs) -> Future:
        """
        Ensures that prepare_session is executed only once at a time for this instance.
        If a session preparation is already in progress for this instance, it returns the existing Future.
        Otherwise, it creates a new Future and runs prepare_session in a separate thread.
        
        Returns:
            Future: A Future object that will be completed when the session preparation is done.
        """
        
        # Use a lock to ensure thread safety when checking and setting _prepare_session_future
        with self._prepare_session_lock:
            # Check if there's already a Future in progress for this instance
            if self._prepare_session_future is not None and not self._prepare_session_future.done():
                self.logger.info("Session preparation already in progress for this instance, returning existing Future")
                return self._prepare_session_future
            
            # Create a new Future using ThreadPoolExecutor
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            self._prepare_session_future = executor.submit(self.prepare_session, **kwargs)
            # Make sure to shutdown the executor when the future is done
            self._prepare_session_future.add_done_callback(lambda _: executor.shutdown(wait=False))
            
            return self._prepare_session_future
    
    def prepare_statement(self, statement: str, **kwargs) -> None:
        self.code_history[str(datetime.datetime.now())] = statement
        while self.code_history and sys.getsizeof(self.code_history) > CODE_HISTORY_MAX_SIZE:
            self.code_history.popitem(last=False)

    
    def get_spark_configurations(self, application_id: str | None) -> Any:
        response_json = self._make_spark_api_request(GET_SPARK_CONFIGURATIONS, application_id=application_id)
        spark_configs = {}
        if response_json and 'sparkProperties' in response_json:
            for i, prop in enumerate(response_json['sparkProperties']):
                if prop[0] in TUNING_SPARK_PROPERTIES:
                    spark_configs[prop[0]] = prop[1]
        return spark_configs
        
    def get_spark_failed_task_details(self, application_id: str | None) -> Any: 
        result = self._make_spark_api_request(GET_SPARK_FAILED_TASKS_DETAILS, application_id=application_id)
        
        # Remove 'host' and 'executorLogs' fields from each task in the tasks dictionary
        if result and isinstance(result, list):
            for stage in result:
                if 'tasks' in stage and isinstance(stage['tasks'], dict):
                    for task_id, task in stage['tasks'].items():
                        if 'host' in task:
                            del task['host']
                        if 'executorLogs' in task:
                            del task['executorLogs']
        
        return result
    
    def get_spark_all_executors(self, application_id: str | None) -> Any:
        result = self._make_spark_api_request(GET_SPARK_ALL_EXECUTORS, application_id=application_id)
        
        # Remove 'attributes', 'hostPort', and 'executorLogs' fields from each executor
        if result and isinstance(result, list):
            for executor in result:
                if 'attributes' in executor:
                    del executor['attributes']
                if 'hostPort' in executor:
                    del executor['hostPort']
                if 'executorLogs' in executor:
                    del executor['executorLogs']
        
        return result
    
    def get_spark_failed_jobs(self, application_id: str | None) -> Any:
        return self._make_spark_api_request(GET_SPARK_FAILED_JOBS, application_id=application_id)
    
    def get_spark_unknown_jobs(self, application_id: str | None) -> Any:
        return self._make_spark_api_request(GET_SPARK_UNKNOWN_JOBS, application_id=application_id)
    
    def _make_spark_api_request(self, request_name: str, application_id: str|None) -> Any:
        if self.request_session is None or self.spark_ui_base_url is None:
            try:
                future = self.prepare_session_in_seperate_thread()
                # Wait for the future to complete
                future.result()
            except Exception as e:
                self.logger.error(f"Error preparing session: {e}")
        
        if self.request_session is None:
            self.logger.error("Failed to initialize request_session")
            return {}
            
        if self.spark_ui_base_url is None:
            self.logger.error("Failed to initialize spark_ui_base_url")
            return {}
            
        try:
            response = self.request_session.get(self._get_url_from_task_name(request_name, application_id))
            
            if response.status_code == 403:
                self.logger.info("Received 403 Forbidden, refreshing session and retrying...")
                response.close() 
                
                try:
                    future = self.prepare_session_in_seperate_thread()
                    future.result()
                except Exception as e:
                    self.logger.error(f"Error preparing session: {e}")
                
                if self.request_session is None:
                    self.logger.error("Failed to initialize request_session on retry")
                    return {}
                    
                response = self.request_session.get(self._get_url_from_task_name(request_name, application_id))
            
            # Check for 400 status code, in this case it could mean that the application was terminated because of error
            # retry for prepare_session with session_stpped flag on
            if response.status_code == 400:
                self.logger.error(f"HTTP error: {response.status_code}, {response.reason}")
                response.close()
                try:
                    self.session_stopped = True
                    future = self.prepare_session_in_seperate_thread()
                    future.result()
                except Exception as e:
                    self.logger.error(f"Error preparing session: {e}")
                
                if self.request_session is None:
                    self.logger.error("Failed to initialize request_session on retry")
                    return {}
                    
                response = self.request_session.get(self._get_url_from_task_name(request_name, application_id))
            
            if response.status_code != 200:
                self.logger.error(f"HTTP error: {response.status_code}, {response.reason}")
                response.close()
                return {}
                
            content = response.content
            result = json.loads(content)
            response.close()
            return result
        except Exception as e:
            self.logger.error(f"Error in {request_name}: {e}")
            return {}
        
    def get_notebook_path(self) -> str:
        # Ref: https://github.com/jupyter-server/jupyter_server/pull/679/files
        notebook_path = os.getenv('JPY_SESSION_NAME')
        if notebook_path and os.path.exists(notebook_path):
            return notebook_path
        else:
            return ""
        
        
    def get_debugging_info(self, **kwargs) -> Dict[str, asyncio.Task]:
        application_id = kwargs.get('application_id') if kwargs else None
        task_map = {
            "spark_selected_configurations": asyncio.create_task(asyncio.to_thread(self.get_spark_configurations, application_id)),
            "spark_failed_task_details": asyncio.create_task(asyncio.to_thread(self.get_spark_failed_task_details, application_id)),
            "spark_all_executors": asyncio.create_task(asyncio.to_thread(self.get_spark_all_executors, application_id)),
            "spark_failed_jobs": asyncio.create_task(asyncio.to_thread(self.get_spark_failed_jobs, application_id)),
            "spark_unknown_jobs": asyncio.create_task(asyncio.to_thread(self.get_spark_unknown_jobs, application_id))
        }
        return task_map
    
    @abc.abstractmethod
    def _get_url_from_task_name(self, task_name: str, application_id: str | None) -> str:
        pass
        
    async def _get_debugging_info_async(self, **kwargs):
        task_map = self.get_debugging_info(**kwargs)
        result_map = {}
        
        # Process each task individually and handle exceptions for each task separately
        for key, task in task_map.items():
            try:
                result_map[key] = await task
            except Exception as e:
                # If an exception occurs for this task, only set this task's result to an empty dictionary
                self.logger.error(f"Error in _get_debugging_info_async for task {key}: {e}")
                result_map[key] = {}
        
        return result_map
        
    def _write_debugging_info_sync(self, cell_id: str, **kwargs) -> bool:
        directory = kwargs.get('directory', DEFAULT_DEBUGGING_DIR_TEMPLATE.format(cell_id=cell_id))
        error_message = kwargs.get('error_message') if kwargs else ""
        cell_content = kwargs.get('cell_content') if kwargs else ""
        self.get_logger().info(f"Writing debugging info for cell {cell_id}")
        
        # Ensure the directory exists
        if not os.path.exists(directory):
            os.makedirs(directory)
        os.chmod(directory, 0o755)
            
        success_path = f"{directory}/.success" 
        result_map = asyncio.run(self._get_debugging_info_async(**kwargs))
        
        debugging_info = {
            "path_to_notebook": self.get_notebook_path(),
            "failed_cell_id": cell_id,
            "failed_cell_type" : "spark",
            "failed_cell_content" : cell_content,
            "error_message": error_message,
            "session_type" : str(type(self.session)).split(".")[-1].split("'")[0],
            "latest_code_history": self.code_history,
            **result_map
        }
        
        path = f"{directory}/debugging_info.json"
        with open(path, "w") as f:
            json.dump(debugging_info, f, indent=4)
        os.chmod(path, 0o644)

        with open(success_path, "w") as f:
            pass
        os.chmod(success_path, 0o644)
            
        return True
        
    def write_debugging_info(self, cell_id: str, **kwargs):
        # Ensure the DEFAULT_DEBUGGING_DIR_PARENT exists
        if not os.path.exists(DEFAULT_DEBUGGING_DIR_PARENT):
            os.makedirs(DEFAULT_DEBUGGING_DIR_PARENT)
            os.chmod(DEFAULT_DEBUGGING_DIR_PARENT, 0o755)
            
        # Copy the spark_debugging_sop.txt file from prompts directory to DEFAULT_DEBUGGING_DIR_PARENT
        source_sop_path = os.path.join(os.path.dirname(__file__), "prompts", "spark_debugging_sop.txt")
        target_sop_path = os.path.join(DEFAULT_DEBUGGING_DIR_PARENT, "spark_debugging_sop.txt")
        
        if not os.path.exists(target_sop_path) and os.path.exists(source_sop_path):
            shutil.copy(source_sop_path, target_sop_path)
            os.chmod(target_sop_path, 0o644)
            self.get_logger().info(f"Copied spark_debugging_sop.txt to {target_sop_path}")
            
        self._ensure_symlink_exists(DEFAULT_DEBUGGING_DIR_PARENT, SYMLINK_DEBUGGING_DIR_PARENT)
        self.get_logger().info(f"Starting asynchronous write of debugging info for cell {cell_id}...")
        directory = kwargs.get('directory', DEFAULT_DEBUGGING_DIR_TEMPLATE.format(cell_id=cell_id))
        cell_content = kwargs.get('cell_content', "") if kwargs else ""
        
        magic_command = ""
        if cell_content and cell_content.startswith("%%"):
            space_index = cell_content.find(" ")
            if space_index != -1:
                magic_command = cell_content[:space_index]
            else:
                magic_command = cell_content
                
        if not os.path.exists(directory):
            os.makedirs(directory)
        os.chmod(directory, 0o755)
        
        # Clean up old .success file if it exists
        success_path = f"{directory}/.success"
        if os.path.exists(success_path):
            os.remove(success_path)
            
        display({
            'application/sagemaker-interactive-debugging': {
                'cell_id': cell_id,
                "magic_command" : magic_command,
                "session_type" : str(type(self.session)).split(".")[-1].split("'")[0],
                "instruction_file" : os.path.join(SYMLINK_DEBUGGING_DIR_PARENT, "spark_debugging_sop.txt"),
                'debugging_info_folder': SYMLINK_DEBUGGING_DIR_TEMPLATE.format(cell_id=cell_id)
            }
        }, raw=True)
        
        # Create a daemon thread to run the synchronous method
        daemon_thread = threading.Thread(
            target=self._write_debugging_info_sync,
            args=(cell_id,),
            kwargs=kwargs,
            daemon=True
        )
        daemon_thread.start()
        return
    
    def clean_up_request_session(self):
        if self.request_session is not None:
            self.request_session.close()
            self.request_session = None
            
    def _ensure_symlink_exists(self, source_path: str, target_path: str) -> None:        
        # First, ensure source directory exists
        if not os.path.exists(source_path):
            os.makedirs(source_path)
            os.chmod(source_path, 0o755)
            self.get_logger().info(f"Created source directory: {source_path}")
            
        symlink_needs_update = False
        
        if os.path.islink(target_path):
            try:
                current_source = os.readlink(target_path)
                if current_source != source_path:
                    self.get_logger().info(f"Symlink points to incorrect destination: {current_source}, updating...")
                    symlink_needs_update = True
            except OSError as e:
                self.get_logger().warning(f"Error reading symlink: {e}, will recreate it")
                symlink_needs_update = True
        else:
            symlink_needs_update = True
            
        if symlink_needs_update:
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            os.symlink(src=source_path, dst=target_path, target_is_directory=True)
            self.get_logger().info(f"Created symlink from {source_path} to {target_path}")
        else:
            self.get_logger().info(f"Symlink from {source_path} to {target_path} already exists and is correct")
    
    def clean_up(self):
        self.clean_up_request_session()
