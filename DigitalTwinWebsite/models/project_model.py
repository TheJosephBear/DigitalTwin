from flask_mongoengine import MongoEngine

db = MongoEngine()

class Project(db.Document):
    name = db.StringField(required=True, unique=True)

    def to_json(self):
        return {
            "id": str(self.id),
            "name": self.name
        }
