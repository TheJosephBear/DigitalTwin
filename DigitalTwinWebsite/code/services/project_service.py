import os
import shutil   
import uuid
import json

class ProjectService:

    projects_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'projects'))

    @staticmethod
    def upload_editor_data(name, data):
        try:
            project = ProjectService.create_new_project(name)
            file_path = project.get_save_data_path()
            with open(file_path, 'w') as file:
                file.write(data)
            return 200, None
        except Exception as e:
            return 500, None
        
    @staticmethod
    def upload_model(name, files):
        if 'file' not in files:
            return 400
        file = files['file']
        if file.filename == '':
            return 400, None
        try:
            # Use ProjectManager to get or create the project and save the model file
            project = ProjectService.create_new_project(name)
            file_path = project.get_model_path(file.filename)

            # Save the uploaded file to the specified model path
            file.save(file_path)
            return 201, None
        except Exception as e:
            return 500, None

    @staticmethod
    def download_data(name):
        try:
            project = ProjectService.create_new_project(name)
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
    def download_models(project_name, file_name):
        try:
            project = ProjectService.create_new_project(project_name)
            file_path = project.get_model_path(file_name)

            if os.path.exists(file_path):
                return 200, (project.models_dir, file_name)
            else:
                return 404, None
        except Exception as e:
            return 500, None

    @staticmethod
    def create_project_with_data(name, project_id):
        try:
            project = ProjectService.create_new_project(name)
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
    def create_new_project(name):
        """Create a new project and return the Project instance."""
        project = Project(name)
        return project
    
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
        """Rename a project by changing the directory name."""
        try:
            old_path = os.path.join(ProjectService.projects_root, old_name)
            new_path = os.path.join(ProjectService.projects_root, new_name)
            if os.path.exists(old_path):
                os.rename(old_path, new_path)
                return 200, None
            else:
                return 404, None
        except Exception as e:
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
        """Duplicate an existing project directory to a new name."""
        old_path = os.path.join(ProjectService.projects_root, old_name)
        new_path = os.path.join(ProjectService.projects_root, new_name)
        if not os.path.exists(old_path):
            return 404, None
        if os.path.exists(new_path):
            return 409, None
        shutil.copytree(old_path, new_path)
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




class Project:
    def __init__(self, name):
        self.name = name
        self.project_dir = os.path.join(ProjectService.projects_root, name)
        self.models_dir = os.path.join(self.project_dir, 'models')
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

    def get_model_path(self, model_name):
        """Return the path for a specific model file."""
        return os.path.join(self.models_dir, model_name)