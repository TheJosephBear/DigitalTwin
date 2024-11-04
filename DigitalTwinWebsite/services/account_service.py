import bcrypt
from DigitalTwinWebsite.models.user_model import User

class AccountService:
    def register_user(self, username, password):
        if User.objects(login=username).first():
            return None  # User exists

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        user = User(login=username, heslo=hashed_password.decode("utf-8"))
        user.save()
        return user

    def authenticate_user(self, username, password):
        user = User.objects(login=username).first()
        if user and bcrypt.checkpw(password.encode("utf-8"), user.heslo.encode("utf-8")):
            return user
        return None