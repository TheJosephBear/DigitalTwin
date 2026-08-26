import os
import sys
import json
import uuid
import datetime
import argparse
import re
from bson import ObjectId
from dotenv import load_dotenv

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

from repository.mongo_repository import MongoRepository

def resolve_owner_id(repo: MongoRepository, owner_input: str) -> str:
    """
    Converts owner from username to user ID before filling it.
    - If owner_input matches a username in the 'users' collection, returns str(_id).
    - If owner_input is already an ObjectId string or existing user ID, returns it.
    - If not found, returns owner_input and prints a warning.
    """
    if not owner_input:
        return ""

    val = str(owner_input).strip("'\" \t\r\n")
    if not val:
        return ""

    try:
        # Check if there is a user with this username
        user = repo.read_record("users", {"username": val})
        if not user:
            # Case-insensitive fallback
            user = repo.read_record("users", {"username": re.compile(f"^{re.escape(val)}$", re.IGNORECASE)})

        if user:
            converted_id = str(user["_id"])
            return converted_id
    except Exception as e:
        print(f"Error querying users collection for '{val}': {e}")

    # Check if already a valid ObjectId
    try:
        if ObjectId.is_valid(val):
            user_by_id = repo.read_record("users", {"_id": ObjectId(val)})
            if user_by_id:
                return str(user_by_id["_id"])
            return val
    except Exception:
        pass

    print(f"Warning: User '{val}' not found in MongoDB 'users' collection.")
    return val

def fill_mongo_with_projects(owner=None, owner_id=None, default_owner=None, force=False):
    # Support owner, owner_id, or default_owner seamlessly
    effective_owner = owner or owner_id or default_owner
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
    count_skipped = 0

    for name in os.listdir(projects_dir):
        project_path = os.path.join(projects_dir, name)
        if not os.path.isdir(project_path):
            continue

        save_path = os.path.join(project_path, "saveData.txt")
        data = {}
        content = None
        used_enc = None

        if os.path.exists(save_path):
            for enc in ("utf-8", "windows-1250", "cp1250"):
                try:
                    with open(save_path, "r", encoding=enc) as f:
                        content = f.read()
                    used_enc = enc
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue

            if content is not None:
                content_stripped = content.strip()
                if content_stripped:
                    try:
                        data = json.loads(content_stripped)
                    except json.JSONDecodeError:
                        data = {}

        project_name = data.get("projectName") or name
        project_id = data.get("projectId")

        # Check existing project in Mongo
        existing = repo.read_record(collection_name, {"projectName": project_name})
        if not existing:
            existing = repo.read_record(collection_name, {"name": project_name})
        if not existing and name != project_name:
            existing = repo.read_record(collection_name, {"projectName": name})
        if not existing and name != project_name:
            existing = repo.read_record(collection_name, {"name": name})
        if not existing and project_id:
            existing = repo.read_record(collection_name, {"projectId": project_id})

        # Skip projects that are already in mongo unless --force is specified
        if existing and not force:
            count_skipped += 1
            existing_owner = existing.get("owner", "")
            print(f"Skipping project '{project_name}' (already in Mongo, owner: '{existing_owner}')")
            continue

        project_id = project_id or (existing.get("projectId") if existing else None) or str(uuid.uuid4())
        description = data.get("projectDescription") or (existing.get("projectDescription") if existing else "")
        image_id = data.get("projectImageID") or (existing.get("projectImageID") if existing else "")
        owner = data.get("owner", "")

        # When force is active, apply the specified owner to all projects
        if effective_owner and (force or not owner):
            owner = effective_owner

        # Convert owner from username to id before filling it
        resolved_owner = resolve_owner_id(repo, owner)
        if not resolved_owner and existing and "owner" in existing:
            resolved_owner = existing["owner"]

        if owner and resolved_owner != owner:
            print(f"Converted owner '{owner}' -> '{resolved_owner}' for project '{project_name}'")

        if os.path.exists(save_path):
            needs_rewrite = False
            if resolved_owner and data.get("owner") != resolved_owner:
                data["owner"] = resolved_owner
                needs_rewrite = True
            if used_enc and used_enc != "utf-8":
                needs_rewrite = True

            if needs_rewrite:
                try:
                    with open(save_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4)
                    print(f"Updated owner in {save_path} to '{resolved_owner}'")
                except Exception as write_err:
                    print(f"Failed to update owner in {save_path}: {write_err}")

        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        project_doc = {
            "name": project_name,
            "projectName": project_name,
            "projectId": project_id,
            "projectDescription": description,
            "projectImageID": image_id,
            "owner": resolved_owner,
            "updated_at": now
        }

        if existing:
            project_doc["created_at"] = existing.get("created_at", now)
            repo.update_record(collection_name, {"_id": existing["_id"]}, project_doc)
            count_updated += 1
            print(f"Updated project in Mongo: {project_name} (owner: '{resolved_owner}')")
        else:
            project_doc["created_at"] = now
            repo.create_record(collection_name, project_doc)
            count_created += 1
            print(f"Created project in Mongo: {project_name} (owner: '{resolved_owner}')")

    print(f"\nDone! Created: {count_created}, Updated: {count_updated}, Skipped: {count_skipped}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill MongoDB with projects from disk")
    parser.add_argument("--owner", "--owner_id", "--owner-id", dest="owner", type=str, default=None, help="User ID or username to assign as owner")
    parser.add_argument("owner_pos", nargs="?", default=None, help="Optional positional User ID or username")
    parser.add_argument("--force", "-f", action="store_true", default=False, help="Apply the owner to all projects regardless of status (updates existing projects in Mongo)")
    args = parser.parse_args()

    effective_owner = args.owner or args.owner_pos

    fill_mongo_with_projects(owner=effective_owner, force=args.force)
