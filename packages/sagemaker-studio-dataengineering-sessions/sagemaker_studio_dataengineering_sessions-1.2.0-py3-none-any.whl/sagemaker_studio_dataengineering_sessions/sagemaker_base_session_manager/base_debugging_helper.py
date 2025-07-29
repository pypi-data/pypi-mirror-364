"""
Base debugging helper interface for SageMaker Studio Data Engineering Sessions.

This module provides an abstract base class that defines the interface for debugging helpers
used across different session managers.
"""

import abc
import logging
from typing import Any, Dict


class BaseDebuggingHelper(metaclass=abc.ABCMeta):

    """
    Abstract base class for debugging helpers.
    
    This interface defines the contract that all debugging helper implementations
    must follow, providing methods for retrieving and writing debugging information.
    """

    def prepare_session(self, **kwargs):
        pass

    def prepare_statement(self, statement: str, **kwargs) -> None:
        pass

    def get_logger(self):
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(__name__)
        return self._logger
    
    @abc.abstractmethod
    def clean_up(self):
        pass

    @abc.abstractmethod
    def get_debugging_info(self, **kwargs) -> Dict[str, Any]:
        """
        Retrieve debugging information for a session.
        
        Args:
            **kwargs: Additional parameters specific to the implementation.
            
        Returns:
            Dict[str, Any]: A dictionary containing debugging information with keys
                          representing different aspects of the system/session state.
                          
        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
        raise NotImplementedError("get_debugging_info must be implemented")

    @abc.abstractmethod
    def write_debugging_info(self, 
                             cell_id: str,
                             **kwargs):
        raise NotImplementedError("write_debugging_info must be implemented")
    

