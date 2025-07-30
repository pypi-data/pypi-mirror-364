"""
SQLite plugin implementation.
"""
import logging
from typing import Any, Dict, List
from pathlib import Path

from ..core.interfaces import DbPlugin, DbAdapter
from ..core.registry import register_plugin
from ..adapters.sqlite import SQLiteAdapter

logger = logging.getLogger(__name__)


@register_plugin("sqlite")
class SQLitePlugin(DbPlugin):
    """
    SQLite database plugin implementation.
    """
    
    plugin_name = "SQLite Plugin"
    plugin_version = "1.0.0"
    supported_db_types = ["sqlite", "sqlite3"]
    required_dependencies = ["SQLAlchemy"]
    
    def __init__(self, db_root_path: str, db_mode: str = "dev", **kwargs):
        super().__init__(db_root_path, db_mode, **kwargs)
        self.db_id = None
        self.db_directory_path = None
        self.database_path = None
        
        # LSH manager integration (for backward compatibility)
        self._lsh_manager = None
    
    def create_adapter(self, **kwargs) -> DbAdapter:
        """Create and return a SQLite adapter instance"""
        return SQLiteAdapter(kwargs)
    
    def validate_connection_params(self, **kwargs) -> bool:
        """Validate connection parameters for SQLite"""
        # For SQLite, we need either database_path or database_name
        database_path = kwargs.get('database_path')
        database_name = kwargs.get('database_name')
        
        if not database_path and not database_name:
            logger.error("Either 'database_path' or 'database_name' is required for SQLite")
            return False
        
        if database_path:
            # Validate that the path is a string
            if not isinstance(database_path, str):
                logger.error("database_path must be a string")
                return False
            
            # Check if parent directory exists or can be created
            try:
                db_path = Path(database_path)
                db_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(f"Cannot create directory for database path {database_path}: {e}")
                return False
        
        if database_name:
            if not isinstance(database_name, str) or not database_name.strip():
                logger.error("database_name must be a non-empty string")
                return False
        
        return True
    
    def initialize(self, **kwargs) -> None:
        """Initialize the SQLite plugin"""
        # Handle database path resolution
        database_path = kwargs.get('database_path')
        database_name = kwargs.get('database_name')
        
        if not database_path and database_name:
            # Create database path from name and root path
            db_root = Path(self.db_root_path)
            db_dir = db_root / f"{self.db_mode}_databases" / database_name
            db_dir.mkdir(parents=True, exist_ok=True)
            database_path = str(db_dir / f"{database_name}.db")
            kwargs['database_path'] = database_path
        
        # Set database path for adapter
        self.database_path = database_path
        
        # Initialize with updated kwargs
        super().initialize(**kwargs)
        
        # Set up database directory path and ID
        if database_name:
            self.db_id = database_name
        else:
            # Extract database name from path
            self.db_id = Path(database_path).stem
        
        self._setup_directory_path(self.db_id)
        
        logger.info(f"SQLite plugin initialized for database: {self.db_id} at {self.database_path}")
    
    def _setup_directory_path(self, db_id: str) -> None:
        """Set up the database directory path"""
        if isinstance(self.db_root_path, str):
            self.db_root_path = Path(self.db_root_path)
        
        self.db_directory_path = Path(self.db_root_path) / f"{self.db_mode}_databases" / db_id
        self.db_id = db_id
        
        # Reset LSH manager when directory path changes
        self._lsh_manager = None
    
    @property
    def lsh_manager(self):
        """Lazy load LSH manager for backward compatibility"""
        if self._lsh_manager is None and self.db_directory_path:
            from ..lsh.manager import LshManager
            self._lsh_manager = LshManager(self.db_directory_path)
        return self._lsh_manager
    
    # LSH integration methods for backward compatibility
    def set_lsh(self) -> str:
        """Set LSH for backward compatibility"""
        try:
            if self.lsh_manager and self.lsh_manager.load_lsh():
                return "success"
            else:
                return "error"
        except Exception as e:
            logger.error(f"Error loading LSH: {e}")
            return "error"
    
    def query_lsh(self, keyword: str, signature_size: int = 30, n_gram: int = 3, top_n: int = 10) -> Dict[str, Dict[str, List[str]]]:
        """Query LSH for backward compatibility"""
        if self.lsh_manager:
            try:
                return self.lsh_manager.query(
                    keyword=keyword,
                    signature_size=signature_size,
                    n_gram=n_gram,
                    top_n=top_n
                )
            except Exception as e:
                logger.error(f"LSH query failed: {e}")
                raise Exception(f"Error querying LSH for {self.db_id}: {e}")
        else:
            raise Exception(f"LSH not available for {self.db_id}")
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information"""
        base_info = super().get_plugin_info()
        
        if self.adapter:
            adapter_info = self.adapter.get_connection_info()
            base_info.update(adapter_info)
        
        base_info.update({
            "db_id": self.db_id,
            "database_path": self.database_path,
            "db_directory_path": str(self.db_directory_path) if self.db_directory_path else None,
            "lsh_available": self.lsh_manager is not None
        })
        
        return base_info
    
    def get_example_data(self, table_name: str, number_of_rows: int = 30) -> Dict[str, List[Any]]:
        """Get example data through adapter"""
        if self.adapter:
            return self.adapter.get_example_data(table_name, number_of_rows)
        else:
            raise RuntimeError("Plugin not initialized")
