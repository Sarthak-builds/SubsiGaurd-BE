"""
In-memory data storage service for temporary file and result storage.
Thread-safe implementation using locks.
"""
import threading
from typing import Dict, Optional, Any
import pandas as pd


class DataStorage:
    """Thread-safe in-memory storage for uploaded data and analysis results."""
    
    def __init__(self):
        self._data_store: Dict[str, pd.DataFrame] = {}
        self._results_store: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def save_upload(self, file_id: str, df: pd.DataFrame) -> None:
        """
        Store uploaded CSV data.
        
        Args:
            file_id: Unique identifier for the file
            df: Pandas DataFrame containing the uploaded data
        """
        with self._lock:
            self._data_store[file_id] = df.copy()
    
    def get_data(self, file_id: str) -> Optional[pd.DataFrame]:
        """
        Retrieve uploaded data by file ID.
        
        Args:
            file_id: Unique identifier for the file
            
        Returns:
            DataFrame if found, None otherwise
        """
        with self._lock:
            df = self._data_store.get(file_id)
            return df.copy() if df is not None else None
    
    def save_results(self, file_id: str, results: Dict[str, Any]) -> None:
        """
        Store analysis results.
        
        Args:
            file_id: Unique identifier for the file
            results: Analysis results dictionary
        """
        with self._lock:
            self._results_store[file_id] = results.copy()
    
    def get_results(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve analysis results by file ID.
        
        Args:
            file_id: Unique identifier for the file
            
        Returns:
            Results dictionary if found, None otherwise
        """
        with self._lock:
            results = self._results_store.get(file_id)
            return results.copy() if results is not None else None
    
    def delete_data(self, file_id: str) -> bool:
        """
        Delete data and results for a file ID.
        
        Args:
            file_id: Unique identifier for the file
            
        Returns:
            True if data was deleted, False if not found
        """
        with self._lock:
            data_existed = file_id in self._data_store
            results_existed = file_id in self._results_store
            
            if data_existed:
                del self._data_store[file_id]
            if results_existed:
                del self._results_store[file_id]
            
            return data_existed or results_existed
    
    def get_all_file_ids(self) -> list[str]:
        """
        Get list of all stored file IDs.
        
        Returns:
            List of file IDs
        """
        with self._lock:
            return list(self._data_store.keys())


# Global singleton instance
storage = DataStorage()
