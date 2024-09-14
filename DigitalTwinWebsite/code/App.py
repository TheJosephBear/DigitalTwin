from flask import Flask, render_template, request, session, flash, redirect, url_for, get_flashed_messages, jsonify, abort, make_response, send_file, send_from_directory, abort, jsonify
import os
import zipfile
import io
from fileinput import filename 
from flask_cors import CORS, cross_origin
from ProjectManager import ProjectManager, Project

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

@app.route("/")
def home():
    return render_template("main.html")

@app.route('/upload_editor_data', methods=['POST'])
def upload_editor_data():
    project_name = request.form['projectName']
    received_data = request.form['myData']

    # Use ProjectManager to get the project and save the data
    project = ProjectManager.create_new_project(project_name)
    file_path = project.get_save_data_path()

    with open(file_path, 'w') as file:
        file.write(received_data)

    data = {'message': 'Done', 'code': 'SUCCESS'}
    return make_response(jsonify(data), 201)


@app.route('/upload_model_files', methods=['POST'])
def upload_model_files():
    project_name = request.form['projectName']
    f = request.files['file']

    # Use ProjectManager to get the project and save the model file
    project = ProjectManager.create_new_project(project_name)
    file_path = project.get_model_path(f.filename)

    f.save(file_path)
    data = {'message': 'Done', 'code': 'SUCCESS'}
    return make_response(jsonify(data), 201)


@app.route("/download")
@cross_origin(origin='http://127.0.0.1:5001')
def download():
    project_name = request.args.get('projectName')

    # Get the project and file path
    project = ProjectManager.create_new_project(project_name)
    file_path = project.get_save_data_path()

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        abort(404, description="File not found")


@app.route("/downloadModels")
@cross_origin(origin='http://127.0.0.1:5001')
def downloadModels():
    project_name = request.args.get('projectName')
    file_name = request.args.get('fileName')
    project = ProjectManager.create_new_project(project_name)
    file_path = project.get_model_path(file_name)

    if os.path.exists(file_path):
        return send_from_directory(project.models_dir, file_name, as_attachment=True)
    else:
        abort(404, description="File not found")

@app.route('/createProject', methods=['POST'])
def create_project():
    project_name = request.form['projectName']
    
    # Check if the project already exists
    project_path = os.path.join(ProjectManager.projects_root, project_name)
    if os.path.exists(project_path):
        return make_response(jsonify({'message': 'Project already exists', 'code': 'ERROR'}), 409)
    
    # Create the new project
    project = ProjectManager.create_new_project(project_name)
    
    data = {'message': 'Project created', 'code': 'SUCCESS'}
    return make_response(jsonify(data), 201)


@app.route('/editProjectName', methods=['PUT'])
def edit_project_name():
    old_name = request.form['oldProjectName']
    new_name = request.form['newProjectName']
    
    try:
        # Edit the project name
        ProjectManager.edit_project_name(old_name, new_name)
        data = {'message': 'Project name updated', 'code': 'SUCCESS'}
        return make_response(jsonify(data), 200)
    except FileNotFoundError:
        return make_response(jsonify({'message': 'Project not found', 'code': 'ERROR'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': str(e), 'code': 'ERROR'}), 500)


@app.route('/deleteProject', methods=['DELETE'])
def delete_project():
    project_name = request.form['projectName']
    
    try:
        # Delete the project
        ProjectManager.delete_project(project_name)
        data = {'message': 'Project deleted', 'code': 'SUCCESS'}
        return make_response(jsonify(data), 200)
    except FileNotFoundError:
        return make_response(jsonify({'message': 'Project not found', 'code': 'ERROR'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': str(e), 'code': 'ERROR'}), 500)

@app.route('/getAllProjects', methods=['GET'])
def get_all_projects():
    projects_root = os.path.join(os.path.dirname(__file__), 'projects')
    
    # List all directories in the project root
    try:
        project_names = [name for name in os.listdir(projects_root) if os.path.isdir(os.path.join(projects_root, name))]
        
        data = {'projects': project_names, 'code': 'SUCCESS'}
        return make_response(jsonify(data), 200)
    
    except Exception as e:
        return make_response(jsonify({'message': str(e), 'code': 'ERROR'}), 500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)