import os
import shutil
import uuid
import json

class ProjectService:

    projects_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'projects'))
    SURVEY_COLLECTION = "surveys"

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
    def create_project_with_data(name, project_id):
        try:
            project = Project(name, create=True)
            file_path = project.get_save_data_path()

            data = {
                "projectName": name,
                "projectId": project_id
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
                    json.dump(data, f)

            return 200, None
        except Exception:
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
                json.dump(data, f)

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
                                "projectId": data.get("projectId")
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
