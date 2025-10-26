# CRUD_Python_Module.py
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure, PyMongoError

class AnimalShelter:
    """CRUD helper for the AAC database."""

    def __init__(
        self,
        username: str = "",
        password: str = "",
        host: str = "127.0.0.1",
        port: int = 27017,
        db_name: str = "aac",
        collection_name: str = "animals",
        auth_source: Optional[str] = None,
        server_selection_timeout_ms: int = 5000,
    ) -> None:

        if not auth_source:
            auth_source = db_name

        # Allow connection with or without credentials
        if username and password:
            user_enc = quote_plus(username)
            pwd_enc = quote_plus(password)
            uri = f"mongodb://{user_enc}:{pwd_enc}@{host}:{port}/{db_name}?authSource={auth_source}"
        else:
            uri = f"mongodb://{host}:{port}/{db_name}"

        self._client = MongoClient(uri, serverSelectionTimeoutMS=server_selection_timeout_ms)
        try:
            self._client.admin.command("ping")
            print(f"✅ Connected to MongoDB at {host}:{port}, database: {db_name}")
        except ConnectionFailure as e:
            raise ConnectionFailure(f"❌ Cannot connect to MongoDB: {e}")
        except OperationFailure as e:
            raise OperationFailure(f"❌ Authentication failed: {e}")

        self._db = self._client[db_name]
        self._collection = self._db[collection_name]

    # Create
    def create(self, data: Dict[str, Any]) -> bool:
        if not isinstance(data, dict) or not data:
            return False
        try:
            self._collection.insert_one(data)
            return True
        except PyMongoError:
            return False

    # Read
    def read(self, query: Optional[Dict[str, Any]] = None, projection: Optional[Dict[str, int]] = None) -> List[Dict[str, Any]]:
        try:
            if query is None:
                query = {}
            if projection is None:
                projection = {"_id": 0}
            return list(self._collection.find(query, projection))
        except PyMongoError:
            return []

    # Update
    def update(self, query: Dict[str, Any], new_values: Dict[str, Any]) -> int:
        try:
            result = self._collection.update_many(query, {"$set": new_values})
            return result.modified_count
        except PyMongoError:
            return 0

    # Delete
    def delete(self, query: Dict[str, Any]) -> int:
        try:
            result = self._collection.delete_many(query)
            return result.deleted_count
        except PyMongoError:
            return 0
