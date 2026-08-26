import os
import sys
import json
import argparse
from dotenv import load_dotenv

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

from repository.mongo_repository import MongoRepository

def migrate_project_surveys(db):
    """
    Recalculates hasSurvey and respondentCount directly in the projects collection.
    """
    projects = db.projects.find()
    migrated_count = 0

    for proj in projects:
        name = proj.get("projectName") or proj.get("name")
        if not name:
            continue

        # Count existing responses
        resp_count = db.survey_responses.count_documents({"project_name": name})

        # Check survey document and questions
        survey_doc = db.surveys.find_one({"project_name": name})
        has_survey = False
        if survey_doc:
            s_data = survey_doc.get("survey_data", {})
            if isinstance(s_data, str):
                try:
                    s_data = json.loads(s_data)
                except Exception:
                    s_data = {}
            questions = []
            if isinstance(s_data, dict):
                questions = s_data.get("Questions") or s_data.get("questions") or []
            elif isinstance(s_data, list):
                questions = s_data
            has_survey = (isinstance(questions, list) and len(questions) > 0) or resp_count > 0

        db.projects.update_one(
            {"_id": proj["_id"]},
            {
                "$set": {
                    "hasSurvey": bool(has_survey),
                    "respondentCount": int(resp_count)
                }
            }
        )
        migrated_count += 1
        print(f"Project '{name}': hasSurvey={has_survey}, respondentCount={resp_count}")

    print(f"Migration completed. Total projects processed: {migrated_count}")
    return migrated_count


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(base_dir, "..", ".."))

    env_local = os.path.join(root_dir, ".env.local")
    env_default = os.path.join(root_dir, ".env")
    if os.path.exists(env_local):
        load_dotenv(env_local)
    elif os.path.exists(env_default):
        load_dotenv(env_default)
    else:
        load_dotenv()

    db_name = os.getenv("MONGO_DBNAME")
    if db_name:
        db_name = db_name.strip("'\" \t\r\n")
    if not db_name:
        db_name = "digitalTwin"
        config_path = os.path.join(os.path.dirname(base_dir), "conf.toml")
        if os.path.exists(config_path) and tomllib is not None:
            with open(config_path, "rb") as f:
                config = tomllib.load(f)
                db_name = config.get("database", {}).get("database_name", db_name)
    if db_name:
        db_name = db_name.strip("'\" \t\r\n")

    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    if mongo_uri:
        mongo_uri = mongo_uri.strip("'\" \t\r\n")

    print(f"Connecting to MongoDB at {mongo_uri}, database: {db_name}")
    repo = MongoRepository(uri=mongo_uri, database_name=db_name)
    repo.connect_to_database()

    migrate_project_surveys(repo.db)


if __name__ == "__main__":
    main()
