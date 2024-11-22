from typing import Protocol, Any

class Repository(Protocol):
    def connect_to_database(self) -> None:
        """Establish connection to the database."""
        ...

    def create_record(self, collection_name: str, data: dict) -> Any:
        """Insert a new record into the database."""
        ...

    def read_record(self, collection_name: str, query: dict) -> Any:
        """Read a record from the database matching the query."""
        ...

    def update_record(self, collection_name: str, query: dict, update_data: dict) -> None:
        """Update an existing record in the database."""
        ...

    def delete_record(self, collection_name: str, query: dict) -> None:
        """Delete a record from the database."""
        ...

    def read_all_records(self, collection_name: str) -> list[dict]:
        """Read all records from the table."""
        ...
