"""
Qdrant adapter for Thoth SQL Database Manager.
"""

from typing import Any, Dict, List, Optional, Union
from ..core.interfaces import DbAdapter


class QdrantAdapter(DbAdapter):
    """
    Qdrant vector database adapter implementation.
    """
    
    def __init__(self, **kwargs):
        """Initialize Qdrant adapter with connection parameters."""
        super().__init__()
        self.host = kwargs.get('host', 'localhost')
        self.port = kwargs.get('port', 6333)
        self.api_key = kwargs.get('api_key')
        self.collection_name = kwargs.get('collection_name', 'thoth_documents')
        self._client = None
    
    def connect(self) -> bool:
        """Establish connection to Qdrant."""
        try:
            # Import qdrant_client here to avoid dependency issues
            from qdrant_client import QdrantClient
            
            if self.api_key:
                self._client = QdrantClient(
                    host=self.host,
                    port=self.port,
                    api_key=self.api_key
                )
            else:
                self._client = QdrantClient(
                    host=self.host,
                    port=self.port
                )
            
            # Test connection
            self._client.get_collections()
            return True
        except Exception as e:
            print(f"Failed to connect to Qdrant: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from Qdrant."""
        if self._client:
            self._client.close()
            self._client = None
    
    def execute_query(self, query: str, params: Optional[Dict] = None, 
                     fetch: Union[str, int] = "all", timeout: int = 60) -> Any:
        """
        Execute a query against Qdrant.
        Note: Qdrant doesn't use SQL, so this adapts the interface.
        """
        if not self._client:
            raise RuntimeError("Not connected to Qdrant")
        
        # This is a placeholder - adapt based on your specific needs
        # Qdrant uses vector search, not SQL queries
        return {"message": "Qdrant uses vector search, not SQL queries"}
    
    def get_tables(self) -> List[Dict[str, str]]:
        """Get collections (equivalent to tables in Qdrant)."""
        if not self._client:
            raise RuntimeError("Not connected to Qdrant")
        
        try:
            collections = self._client.get_collections()
            return [
                {
                    "table_name": collection.name,
                    "table_type": "COLLECTION"
                }
                for collection in collections.collections
            ]
        except Exception as e:
            print(f"Error getting collections: {e}")
            return []
    
    def get_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Get collection info (equivalent to columns in Qdrant)."""
        if not self._client:
            raise RuntimeError("Not connected to Qdrant")
        
        try:
            collection_info = self._client.get_collection(table_name)
            return [
                {
                    "column_name": "id",
                    "data_type": "UUID",
                    "is_nullable": False
                },
                {
                    "column_name": "vector",
                    "data_type": f"VECTOR({collection_info.config.params.vectors.size})",
                    "is_nullable": False
                },
                {
                    "column_name": "payload",
                    "data_type": "JSON",
                    "is_nullable": True
                }
            ]
        except Exception as e:
            print(f"Error getting collection info: {e}")
            return []
    
    def get_foreign_keys(self) -> List[Dict[str, str]]:
        """Get foreign keys (not applicable for Qdrant)."""
        return []
    
    def get_unique_values(self) -> Dict[str, Dict[str, List[str]]]:
        """Get unique values from collections."""
        if not self._client:
            raise RuntimeError("Not connected to Qdrant")
        
        # This is a simplified implementation
        # In practice, you'd need to scroll through points and extract unique payload values
        return {}
    
    def add_documentation(self, doc_type: str, content: Dict[str, Any]) -> str:
        """Add documentation to Qdrant collection."""
        if not self._client:
            raise RuntimeError("Not connected to Qdrant")
        
        try:
            from qdrant_client.models import PointStruct
            import uuid
            
            # Generate a unique ID for the document
            doc_id = str(uuid.uuid4())
            
            # Create a point with the documentation content
            point = PointStruct(
                id=doc_id,
                vector=content.get('vector', [0.0] * 384),  # Default vector size
                payload={
                    "doc_type": doc_type,
                    "content": content
                }
            )
            
            # Upsert the point
            self._client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            return doc_id
        except Exception as e:
            print(f"Error adding documentation: {e}")
            raise
    
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection from Qdrant."""
        if not self._client:
            raise RuntimeError("Not connected to Qdrant")
        
        try:
            self._client.delete_collection(collection_name)
            return True
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False
    
    def create_collection(self, collection_name: str, vector_size: int = 384) -> bool:
        """Create a new collection in Qdrant."""
        if not self._client:
            raise RuntimeError("Not connected to Qdrant")
        
        try:
            from qdrant_client.models import VectorParams, Distance
            
            self._client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            return True
        except Exception as e:
            print(f"Error creating collection: {e}")
            return False