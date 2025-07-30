"""
Qdrant plugin for Thoth SQL Database Manager.
"""

from typing import List
from ..core.interfaces import DbPlugin
from ..adapters.qdrant import QdrantAdapter


class QdrantPlugin(DbPlugin):
    """Plugin for Qdrant vector database."""
    
    plugin_name = "qdrant"
    plugin_version = "1.0.0"
    supported_db_types = ["qdrant"]
    required_dependencies = ["qdrant-client"]
    
    def create_adapter(self, **kwargs) -> QdrantAdapter:
        """Create and return a QdrantAdapter instance."""
        return QdrantAdapter(**kwargs)
    
    def validate_connection_params(self, **kwargs) -> bool:
        """Validate Qdrant connection parameters."""
        required_params = ['host']
        
        for param in required_params:
            if param not in kwargs:
                return False
        
        # Validate host format
        host = kwargs.get('host')
        if not isinstance(host, str) or not host.strip():
            return False
        
        # Validate port if provided
        port = kwargs.get('port')
        if port is not None:
            if not isinstance(port, int) or port <= 0 or port > 65535:
                return False
        
        return True