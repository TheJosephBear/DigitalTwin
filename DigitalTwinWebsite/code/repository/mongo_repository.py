from pymongo import MongoClient
from repository.repositoryClass import Repository

class MongoRepository(Repository):
    def __init__(self, uri: str = "mongodb://localhost:27017", database_name: str = "digitalTwin"):
        self.uri = uri
        self.database_name = database_name
        self.client = None
        self.db = None

    def connect_to_database(self):
        """Establishes a connection to the MongoDB database."""
        if not self.client:
            self.client = MongoClient(self.uri, connect=True)
            self.db = self.client[self.database_name]
            print(f"Connected to database: {self.database_name}")

    def create_record(self, collection_name: str, data: dict):
        """Inserts a single document into the specified collection."""
        self.connect_to_database()
        return self.db[collection_name].insert_one(data).inserted_id

    def read_record(self, collection_name: str, query: dict):
        """Finds a single document matching the query."""
        self.connect_to_database()
        return self.db[collection_name].find_one(query)

    def update_record(self, collection_name: str, query: dict, update_data: dict):
        """Updates documents matching the query with new data."""
        self.connect_to_database()
        result = self.db[collection_name].update_many(query, {"$set": update_data})
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    def delete_record(self, collection_name: str, query: dict):
        """Deletes documents matching the query."""
        self.connect_to_database()
        result = self.db[collection_name].delete_many(query)
        return {"deleted_count": result.deleted_count}

    def read_all_records(self, collection_name: str):
        """Returns a collection object for more advanced operations."""
        self.connect_to_database()
        return self.db[collection_name]
