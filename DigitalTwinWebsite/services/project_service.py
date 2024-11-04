import os
from DigitalTwinWebsite.models.project_model import Project

class ProjectService:
    projects_root = 'projects'

    @staticmethod
    def create_project(project_name):
        if Project.objects(name=project_name).first():
            return None  # Project already exists
        
        project = Project(name=project_name)
        project.save()
        os.makedirs(os.path.join(ProjectService.projects_root, project_name), exist_ok=True)
        return project

    @staticmethod
    def get_all_projects():
        return [project.to_json() for project in Project.objects]

    @staticmethod
    def delete_project(project_name):
        project = Project.objects(name=project_name).first()
        if project:
            project_path = os.path.join(ProjectService.projects_root, project_name)
            if os.path.isdir(project_path):
                os.rmdir(project_path)
            project.delete()
            return True
        return False