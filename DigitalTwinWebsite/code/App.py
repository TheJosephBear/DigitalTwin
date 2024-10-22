from flask import Flask, render_template, request, session, flash, redirect, url_for, get_flashed_messages, jsonify, abort, make_response, send_file, send_from_directory, abort, jsonify
import os
import zipfile
import io
import traceback
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
    
    try:
        # Use ProjectManager to get or create the project and save the data
        project = ProjectManager.create_new_project(project_name)
        file_path = project.get_save_data_path()

        # Save the data to the specified file path
        with open(file_path, 'w') as file:
            file.write(received_data)

        data = {'message': 'Editor data saved successfully', 'code': 'SUCCESS'}
        return make_response(jsonify(data), 201)

    except Exception as e:
        return make_response(jsonify({'message': str(e), 'code': 'ERROR'}), 500)

@app.route('/upload_model_files', methods=['POST'])
def upload_model_files():
    project_name = request.form['projectName']
    
    if 'file' not in request.files:
        return make_response(jsonify({'message': 'No file part in the request', 'code': 'ERROR'}), 400)
    
    f = request.files['file']

    if f.filename == '':
        return make_response(jsonify({'message': 'No selected file', 'code': 'ERROR'}), 400)
    
    try:
        # Use ProjectManager to get or create the project and save the model file
        project = ProjectManager.create_new_project(project_name)
        file_path = project.get_model_path(f.filename)

        # Save the uploaded file to the specified model path
        f.save(file_path)
        data = {'message': 'Model file uploaded successfully', 'code': 'SUCCESS'}
        return make_response(jsonify(data), 201)

    except Exception as e:
        return make_response(jsonify({'message': str(e), 'code': 'ERROR'}), 500)



@app.route("/download")
@cross_origin(origin='http://127.0.0.1:5001')
def download():
    project_name = request.args.get('projectName').strip()

    try:
        # Get the project and file path
        project = ProjectManager.create_new_project(project_name)
        file_path = project.get_save_data_path()

        # Check if the file exists before attempting to send it
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return abort(404, description="Save data file not found")

    except Exception as e:
        return make_response(jsonify({'message': str(e), 'code': 'ERROR'}), 500)



@app.route("/downloadModels")
@cross_origin(origin='http://127.0.0.1:5001')
def downloadModels():
    project_name = request.args.get('projectName').strip()
    file_name = request.args.get('fileName').strip()
    print(project_name)
    print(file_name)

    try:
        # Get the project and file path for the model
        project = ProjectManager.create_new_project(project_name)
        print(f"created new project: {project}")
        file_path = project.get_model_path(file_name)
        print(f"filepath: {file_path}")

        # Check if the file exists before attempting to send it
        if os.path.exists(file_path):
            print(f"we good path exists")
            return send_from_directory(directory=project.models_dir, path=file_name, as_attachment=True)
        else:
            print(f"aborted, path doesnt exist")
            return abort(404, description="Model file not found")

    except Exception as e:
        error_message = str(e)
        error_trace = traceback.format_exc()
        print(f"Error occurred: {error_message}")
        print(f"Traceback: {error_trace}")
        return make_response(jsonify({'message': error_message, 'code': 'ERROR'}), 500)


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


@app.route('/editProjectName', methods=['POST'])
def edit_project_name():
    old_name = request.form['oldProjectName']
    new_name = request.form['newProjectName']
    
    try:
        # Edit the project name
        print(f"editing the project name {old_name} {new_name}")
        ProjectManager.edit_project_name(old_name, new_name)
        print("updated!")
        data = {'message': 'Project name updated', 'code': 'SUCCESS'}
        return make_response(jsonify(data), 200)
    except FileNotFoundError:
        return make_response(jsonify({'message': 'Project not found', 'code': 'ERROR'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': str(e), 'code': 'ERROR'}), 500)


@app.route('/duplicate_project', methods=['POST'])
def duplicate_project():
    old_name = request.form['projectName']
    new_name = old_name+" -copy"
    
    try:
        # Duplicate the project
        ProjectManager.duplicate_project(old_name, new_name)
        
        data = {'message': 'Project duplicated successfully', 'code': 'SUCCESS'}
        return make_response(jsonify(data), 201)
    except FileNotFoundError:
        return make_response(jsonify({'message': 'Original project not found', 'code': 'ERROR'}), 404)
    except FileExistsError:
        return make_response(jsonify({'message': 'New project name already exists', 'code': 'ERROR'}), 409)
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

@app.route('/generate_iframe', methods=['GET'])
def generate_iframe():
    project_name = request.args.get('projectName').strip()
    
    try:
        # Manually constructing the URL with correct encoding for spaces
        base_url = url_for('static', filename='Unity/ViewerBuild/index.html', _external=True)
        
        # Use urllib.parse.quote to encode the project_name properly, replacing spaces with %20
        from urllib.parse import quote
        encoded_project_name = quote(project_name)  # Encodes spaces as %20
        
        viewer_url = f"{base_url}?projectName={encoded_project_name}"
        
        iframe_code = f'<iframe src="{viewer_url}" width="800" height="600"></iframe>'
        
        # Return the iframe code as a JSON response
        return make_response(jsonify({'iframe_code': iframe_code, 'message': 'Iframe generated successfully', 'code': 'SUCCESS'}), 200)
    
    except Exception as e:
        return make_response(jsonify({'message': str(e), 'code': 'ERROR'}), 500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)