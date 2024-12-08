import bcrypt

class AccountService:
    def __init__(self, repository):
        self._collection_name = "users"
        self._repository = repository

    def find_user_id(self, name, password):
        """
        Finds the user by their login name and checks the password.
        Returns the user's ID if credentials are correct, None otherwise.
        """
        # Fetch the user by login name
        user = self._repository.read_record(self._collection_name, {"login": name})
        if user:
            # Check if the password matches the stored hash
            if bcrypt.checkpw(password.encode("utf-8"), user["heslo"]):
                return user["_id"]
        return None

    def register_new_user(self, name, password):
        """
        Registers a new user with a hashed password.
        Returns True if successful, None if the user already exists.
        """
        # Check if the user already exists
        if self.check_existing_user(name):
            return None  # User already exists

        # Hash the password and prepare the user data
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        register_data = {
            "login": name,
            "heslo": hashed_password
        }

        # Insert the user into the database
        inserted_id = self._repository.create_record(self._collection_name, register_data)
        return inserted_id is not None

    def check_existing_user(self, name):
        """
        Checks if a user with the given login name already exists.
        Returns True if the user exists, False otherwise.
        """
        # Use read_record to check for existence
        user = self._repository.read_record(self._collection_name, {"login": name})
        return user is not None
    
    def try_login(self, sess, name, password):
        try:
            sess = str(self.find_user_id(name, password)) # this entire thing needs an absolute rework
            if sess != "None":
                return 201, None
        except Exception as e:
            return 500, None
        
    def try_register(self, name, password):
        try:
            if not self.check_existing_user(name):
                if self.register_new_user(name, password) == True:
                    return 201, None
                else:
                    return 500, None
            else:
                return 409, None
        except Exception as e:
            return 500, None
