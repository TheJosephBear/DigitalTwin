import os
import sys
import json
import uuid
import datetime
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

def fill_mongo_with_projects(default_owner=None):
    # Load environment variables
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

    # Database configuration
    db_name = os.getenv("MONGO_DBNAME")
    if not db_name:
        db_name = "digitalTwin"
        config_path = os.path.join(os.path.dirname(base_dir), "conf.toml")
        if os.path.exists(config_path) and tomllib is not None:
            with open(config_path, "rb") as f:
                config = tomllib.load(f)
                db_name = config.get("database", {}).get("database_name", db_name)

    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    print(f"Connecting to Mongo at {mongo_uri}, database: {db_name}")

    repo = MongoRepository(uri=mongo_uri, database_name=db_name)
    repo.connect_to_database()

    projects_dir = os.path.join(base_dir, "projects")
    if not os.path.exists(projects_dir):
        print(f"Projects directory not found at: {projects_dir}")
        return

    collection_name = "projects"
    count_created = 0
    count_updated = 0

    for name in os.listdir(projects_dir):
        project_path = os.path.join(projects_dir, name)
        if not os.path.isdir(project_path):
            continue

        save_path = os.path.join(project_path, "saveData.txt")
        data = {}
        if os.path.exists(save_path):
            content = None
            used_enc = None
            for enc in ("utf-8", "windows-1250", "cp1250"):
                try:
                    with open(save_path, "r", encoding=enc) as f:
                        content = f.read()
                    used_enc = enc
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue

            if content is not None:
                # Convert the file on disk to UTF-8 explicitly
                try:
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Converted {save_path} to UTF-8 (read using {used_enc})")
                except Exception as convert_err:
                    print(f"Failed to rewrite {save_path} in UTF-8: {convert_err}")

                content_stripped = content.strip()
                if content_stripped:
                    try:
                        data = json.loads(content_stripped)
                    except json.JSONDecodeError:
                        data = {}

        project_name = data.get("projectName") or name
        project_id = data.get("projectId") or str(uuid.uuid4())
        description = data.get("projectDescription", "")
        image_id = data.get("projectImageID", "")
        owner = data.get("owner", "")
        if not owner and default_owner:
            owner = default_owner
            data["owner"] = owner
            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                print(f"Assigned owner '{default_owner}' to {save_path}")
            except Exception as write_err:
                print(f"Failed to update owner in {save_path}: {write_err}")

        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        project_doc = {
            "name": project_name,
            "projectName": project_name,
            "projectId": project_id,
            "projectDescription": description,
            "projectImageID": image_id,
            "owner": owner,
            "updated_at": now
        }

        # Check existing
        existing = repo.read_record(collection_name, {"projectName": project_name})
        if not existing:
            existing = repo.read_record(collection_name, {"name": project_name})

        if existing:
            # Maintain original owner or created_at if already present
            if not owner and "owner" in existing:
                project_doc["owner"] = existing["owner"]
            if "created_at" in existing:
                project_doc["created_at"] = existing["created_at"]
            else:
                project_doc["created_at"] = now

            repo.update_record(collection_name, {"_id": existing["_id"]}, project_doc)
            count_updated += 1
            print(f"Updated project in Mongo: {project_name}")
        else:
            project_doc["created_at"] = now
            repo.create_record(collection_name, project_doc)
            count_created += 1
            print(f"Created project in Mongo: {project_name}")

    print(f"\nDone! Created: {count_created}, Updated: {count_updated}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill MongoDB with projects from disk")
    parser.add_argument("--owner", type=str, default=None, help="User ID to assign to projects without an owner")
    args = parser.parse_args()

    fill_mongo_with_projects(default_owner=args.owner)
