from flask_mongoengine import MongoEngine

db = MongoEngine()

class User(db.Document):
    login = db.StringField(required=True, unique=True)
    heslo = db.StringField(required=True)  # "heslo" is assumed to be the password field

    def to_json(self):
        return {
            "id": str(self.id),
            "login": self.login
        }