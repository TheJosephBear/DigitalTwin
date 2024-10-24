import bcrypt
from bson import ObjectId
import json

class AccountManager:
    #Account management - login, register logic
    def __init__(self):
        self._db_table_name = "users"
        self._collection = None

    def load_collection(self, database):
        self._collection = database.get_collection(self._db_table_name)

    # If login credentials are correct returns users ID 
    def find_user_id(self, name, password):
        user = self._collection.find_one({"login": name})
        print(f"looking for user: {user}")
        if user:
            print(f"checking password: ")
            if bcrypt.checkpw(password.encode("utf-8"), user["heslo"]):
                 print(f"password correct ")
                 return user["_id"]
        return None
                
    def register_new_user(self, name, password):
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        register_data = {
                "login" : name,
                "heslo" : hashed_password
        }
        insert_result = self._collection.insert_one(register_data)
        if insert_result.inserted_id:
            return True
        return None
    
    # True if there is 1 or more record in cursor, False if there is 0 records in cursor
    def check_existing_user(self, name):
        cursor = self._collection.find_one({'login': name})
        return cursor is not None
