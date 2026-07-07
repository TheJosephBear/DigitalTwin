import os
import shutil
import uuid
import json
import re
from email.header import decode_header

class ProjectService:

    projects_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'projects'))
    SURVEY_COLLECTION = "surveys"

    @staticmethod
    def upload_image(project_name, asset_hash, files):
        try:
            project = ProjectService.load_project(project_name)
            # Create a specific folder for this image hash inside the project
            image_folder = os.path.join(project.project_dir, 'images', asset_hash)
            os.makedirs(image_folder, exist_ok=True)

            for key in files:
                file = files[key]
                if file.filename == '': continue
                
                # Save the file into the hash folder
                file.save(os.path.join(image_folder, sanitize_upload_filename(file.filename)))
            
            return 201, None
        except Exception as e:
            print(f"Upload Image Error: {e}")
            return 500, None

    @staticmethod
    def download_image(project_name, asset_hash):
        try:
            project = ProjectService.load_project(project_name)
            image_folder = os.path.join(project.project_dir, 'images', asset_hash)
            
            if not os.path.exists(image_folder):
                return 404, None

            # Find the first file in that hash directory
            files = [f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]
            if not files:
                return 404, None
                
            return 200, (image_folder, files[0])
        except Exception as e:
            print(f"Download Image Error: {e}")
            return 500, None

    @staticmethod
    def upload_preview_image(project_name, file):
        try:
            project = ProjectService.load_project(project_name)
            if not file or file.filename == '':
                return 400, "No valid file provided"

            # Create a dedicated preview folder inside the project
            preview_folder = os.path.join(project.project_dir, 'preview')
            os.makedirs(preview_folder, exist_ok=True)

            # Clean out any old preview images first to ensure only ONE exists
            for f in os.listdir(preview_folder):
                os.remove(os.path.join(preview_folder, f))

            # Save the new preview image
            file.save(os.path.join(preview_folder, sanitize_upload_filename(file.filename)))
            return 201, None
        except Exception as e:
            print(f"Upload Preview Error: {e}")
            return 500, None

    @staticmethod
    def download_preview_image(project_name):
        try:
            project = ProjectService.load_project(project_name)
            preview_folder = os.path.join(project.project_dir, 'preview')

            if not os.path.exists(preview_folder):
                return 404, None

            files = [f for f in os.listdir(preview_folder) if os.path.isfile(os.path.join(preview_folder, f))]
            if not files:
                return 404, None

            # Returns the folder and the singular preview filename
            return 200, (preview_folder, files[0])
        except Exception as e:
            print(f"Download Preview Error: {e}")
            return 500, None

    @staticmethod
    def upload_editor_data(name, data):
        try:
            project = ProjectService.load_project(name)
            file_path = project.get_save_data_path()
            with open(file_path, 'w') as file:
                file.write(data)
            return 200, None
        except Exception as e:
            return 500, None

    @staticmethod
    def upload_model(project_name, asset_hash, files):
        """
        Uploads all files for a specific asset into the project.
        Creates a folder named after asset_hash inside the project's models directory.
        """
        if not asset_hash:
            return 400, None

        if not files:
            return 400, None

        try:
            # Ensure the project exists
            project = ProjectService.load_project(project_name)

            # Create folder for this asset inside models_dir
            asset_dir = os.path.join(project.models_dir, asset_hash)
            os.makedirs(asset_dir, exist_ok=True)

            # Save all uploaded files in the asset folder
            for key in files:
                file = files[key]
                if file.filename == '':
                    continue
                file_path = os.path.join(asset_dir, file.filename)
                file.save(file_path)

            return 201, None
        except Exception as e:
            print(f"Error uploading model files: {e}")
            return 500, None

    @staticmethod
    def upload_survey_data(repo, project_name, data):
        """Uploads or updates the survey data in MongoDB."""
        try:
            # Parse data if it's a string
            if isinstance(data, str):
                json_data = json.loads(data)
            else:
                json_data = data

            # We use project_name as the unique identifier for the survey
            query = {"project_name": project_name}
            
            # Prepare the document
            survey_document = {
                "project_name": project_name,
                "survey_data": json_data
            }

            # Check if it exists to decide between update or create
            existing = repo.read_record(ProjectService.SURVEY_COLLECTION, query)
            
            if existing:
                repo.update_record(ProjectService.SURVEY_COLLECTION, query, survey_document)
                return 200, "Survey updated"
            else:
                repo.create_record(ProjectService.SURVEY_COLLECTION, survey_document)
                return 201, "Survey created"

        except json.JSONDecodeError:
            return 400, "Invalid JSON format"
        except Exception as e:
            print(f"Error saving survey to Mongo: {e}")
            return 500, str(e)

    @staticmethod
    def download_survey_data(repo, project_name):
        """Retrieves the survey data from MongoDB."""
        try:
            query = {"project_name": project_name}
            record = repo.read_record(ProjectService.SURVEY_COLLECTION, query)
            
            if record:
                # MongoDB returns a dict, we return the survey_data part
                # Note: record['_id'] is an ObjectId, so we return the nested survey_data
                return 200, record.get("survey_data")
            else:
                return 404, "Survey not found"
        except Exception as e:
            print(f"Error fetching survey: {e}")
            return 500, None

    @staticmethod
    def download_data(name):
        try:
            project = ProjectService.load_project(name)
            file_path = project.get_save_data_path()
            print("Filepath is:")
            print(file_path)
            if os.path.exists(file_path):
                print("path does exist")
                with open(file_path, 'r') as file:
                    content = file.read()
                    print("content of file is: "+content)
                    return 200, content
            else:
                return 404, None
        except Exception as e:
            return 500, None

    @staticmethod
    def download_models(project_name, asset_hash, file_name):
        try:
            project = ProjectService.load_project(project_name)

            asset_dir = os.path.join(project.models_dir, asset_hash)
            file_path = os.path.join(asset_dir, file_name)

            if os.path.exists(file_path):
                return 200, (asset_dir, file_name)
            else:
                return 404, None

        except Exception as e:
            return 500, None


    @staticmethod
    def create_project_with_data(name, project_id, description="", image_id=""):
        try:
            project = Project(name, create=True)
            file_path = project.get_save_data_path()

            data = {
                "projectName": name,
                "projectId": project_id,
                "projectDescription": description,
                "projectImageID": image_id
            }
            with open(file_path, "w") as file:
                file.write(json.dumps(data))

            return 201, None
        except Exception:
            return 500, None


    @staticmethod
    def delete_project(name):
        """Delete the project directory and its contents."""
        try:
            project_path = os.path.join(ProjectService.projects_root, name)
            if os.path.exists(project_path):
                shutil.rmtree(project_path)
                return 200, None
            else:
                return 404, None
        except Exception as e:
                return 500, None

    @staticmethod
    def edit_project_name(old_name, new_name):
        try:
            old_path = os.path.join(ProjectService.projects_root, old_name)
            new_path = os.path.join(ProjectService.projects_root, new_name)

            if not os.path.exists(old_path):
                return 404, None

            os.rename(old_path, new_path)

            save_path = os.path.join(new_path, "saveData.txt")
            if os.path.exists(save_path):
                with open(save_path, "r+") as f:
                    data = json.load(f)
                    data["projectName"] = new_name
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f, indent=4)

            return 200, None
        except Exception:
            return 500, None

    @staticmethod
    def edit_project_metadata(old_name, new_name, description, image_id):
        try:
            # Helper function to strip forbidden Windows characters for folder paths
            def sanitize_folder_name(name):
                return re.sub(r'[\\/*?:"<>|]', "", name).strip()

            sanitized_old = sanitize_folder_name(old_name)
            sanitized_new = sanitize_folder_name(new_name)

            old_path = os.path.join(ProjectService.projects_root, sanitized_old)
            new_path = os.path.join(ProjectService.projects_root, sanitized_new)

            if not os.path.exists(old_path):
                print(f"Error: Path does not exist {old_path}")
                return 404, None

            # 1. Handle physical directory rename using sanitized names
            if sanitized_old != sanitized_new:
                if os.path.exists(new_path):
                    return 409, "A project directory with the new name already exists"
                os.rename(old_path, new_path)
                current_project_path = new_path
            else:
                current_project_path = old_path

            # 2. Update the contents of saveData.txt (Allows the raw name with '?')
            save_path = os.path.join(current_project_path, "saveData.txt")
            
            data = {}
            if os.path.exists(save_path):
                with open(save_path, "r") as f:
                    content = f.read().strip()
                    if content:
                        try:
                            data = json.loads(content)
                        except json.JSONDecodeError:
                            data = {}

            # The JSON preserves the beautiful display name, even if it has '?'
            data["projectName"] = new_name  
            data["projectDescription"] = description if description is not None else ""
            data["projectImageID"] = image_id if image_id is not None else ""

            # Overwrite cleanly using 'w'
            with open(save_path, "w") as f:
                json.dump(data, f, indent=4)

            return 200, None
        except Exception as e:
            print(f"Error editing project metadata: {e}")
            return 500, None

    @staticmethod
    def get_project_editor_data(name):
        """Return the save data for a given project."""
        project = Project(name)
        save_data_path = project.get_save_data_path()
        if os.path.exists(save_data_path):
            with open(save_data_path, 'r') as file:
                return file.read()
        else:
            raise FileNotFoundError(f"Save data for project {name} not found")

    @staticmethod
    def duplicate_project(old_name, new_name):
        root = ProjectService.projects_root
        old_path = os.path.join(root, old_name)

        if not os.path.exists(old_path):
            return 404, None

        # Find next free "(n)" name
        index = 1
        while True:
            new_name = f"{old_name} ({index})"
            new_path = os.path.join(root, new_name)
            if not os.path.exists(new_path):
                break
            index += 1

        shutil.copytree(old_path, new_path)

        save_path = os.path.join(new_path, "saveData.txt")
        if os.path.exists(save_path):
            with open(save_path, "r+") as f:
                data = json.load(f)
                data["projectName"] = new_name
                data["projectId"] = str(uuid.uuid4())
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=4)

        return 201, None



    @staticmethod
    def get_all_projects():
        try:
            root = ProjectService.projects_root
            projects = []

            for name in os.listdir(root):
                project_path = os.path.join(root, name)
                if not os.path.isdir(project_path):
                    continue

                save_path = os.path.join(project_path, "saveData.txt")
                if os.path.exists(save_path):
                    with open(save_path, "r") as f:
                        try:
                            data = json.load(f)
                            projects.append({
                                "projectName": data.get("projectName"),
                                "projectId": data.get("projectId"),
                                "projectDescription": data.get("projectDescription", ""),
                                "projectImageID": data.get("projectImageID", "")
                            })
                        except:
                            continue

            return 200, projects  # Return list directly

        except Exception:
            return 500, None


    @staticmethod
    def load_project(name):
        project_path = os.path.join(ProjectService.projects_root, name)
        if not os.path.exists(project_path):
            raise FileNotFoundError
        return Project(name, create=False)


    @staticmethod
    def create_new_project(name):
        return Project(name, create=True)
    
        


class Project:
    def __init__(self, name, create=True):
        self.name = name
        self.project_dir = os.path.join(ProjectService.projects_root, name)
        self.models_dir = os.path.join(self.project_dir, 'models')
        self.images_dir = os.path.join(self.project_dir, 'images')
        if create:
            self.setup_project_directories()


    def setup_project_directories(self):
        """Create the project directory and models directory if they don't exist."""
        if not os.path.exists(self.project_dir):
            print("directory for project data didnt exist, i created a new one")
            os.makedirs(self.project_dir)
        if not os.path.exists(self.models_dir):
            print("directory for project models didnt exist, i created a new one")
            os.makedirs(self.models_dir)
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)

        save_path = self.get_save_data_path()
        if not os.path.exists(self.get_save_data_path()):
            with open(save_path, 'w') as f:
                f.write("")

    def get_save_data_path(self):
        """Return the path for the saveData.txt file."""
        return os.path.join(self.project_dir, 'saveData.txt')

    def get_model_path(self, asset_hash, file_name):
        """
        Return full path to a specific file inside an asset folder.
        """
        return os.path.join(self.get_asset_folder_path(asset_hash), file_name)

    def get_asset_folder_path(self, asset_hash):
        """
        Return the folder path for a given asset inside the models directory.
        """
        return os.path.join(self.models_dir, asset_hash)
    
    def get_survey_data_path(self):
        """Return the path for the survey.txt file."""
        return os.path.join(self.project_dir, 'survey.json')


def sanitize_upload_filename(raw_filename):
    """Decodes RFC 2047 MIME encoding used by Unity for non-ASCII filenames."""
    if not raw_filename:
        return ""
    try:
        decoded_parts = decode_header(raw_filename)
        filename_parts = []
        for text, encoding in decoded_parts:
            if isinstance(text, bytes):
                filename_parts.append(text.decode(encoding or 'utf-8', errors='ignore'))
            else:
                filename_parts.append(text)
        return "".join(filename_parts)
    except Exception:
        return raw_filename  # Fallback to original if decoding fails