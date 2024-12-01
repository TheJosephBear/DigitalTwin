from flask import Flask, request, session, render_template, make_response, jsonify, url_for, send_file, send_from_directory, abort, g
import os
from dotenv import load_dotenv
import tomli
from flask_cors import CORS, cross_origin
from services.project_service import ProjectService
from services.account_service import AccountService
from tools import tools
from repository.mongo_repository import MongoRepository

app = Flask(__name__)
CORS(app)
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")

config_path = os.path.join(os.path.dirname(__file__), "../conf.toml")
with open(config_path, "rb") as file:
    config = tomli.load(file)

repo = MongoRepository(uri=os.getenv("DB_URL"), database_name=config["database"]["database_name"])
account_service = AccountService(repo)


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

@app.route('/upload_editor_data', methods=['POST'])
def upload_editor_data():
    project_name = request.form.get("project_name")
    received_data = request.form.get("myData") 

    service_response, service_data = ProjectService.upload_editor_data(project_name, received_data)
    
    if  service_response== 200:
        data = {'message': config["server_responses"]["success"], 'code': 'SUCCESS'}
        return make_response(jsonify(data), 201)
    else:
        try_response_error_codes(service_response)


@app.route('/upload_model_files', methods=['POST'])
def upload_model_files():
    project_name = request.form.get("project_name")

    service_response, service_data = ProjectService.upload_model(project_name, request.files)

    if service_response == 201:
        data = {'message': config["server_responses"]["success"], 'code': 'SUCCESS'}
        return make_response(jsonify(data), 201)
    else:
        try_response_error_codes(service_response)
    

@app.route("/download")
@cross_origin(origin='http://127.0.0.1:5001')
def download():
    project_name = request.args.get('project_name').strip()

    service_response, service_data = ProjectService.download_data(project_name)

    if service_response == 200:
        data = service_data
        return make_response(data, 200)
    else:
        try_response_error_codes(service_response)


@app.route("/downloadModels")
@cross_origin(origin='http://127.0.0.1:5001')
def downloadModels():
    project_name = request.args.get('project_name').strip()
    file_name = request.args.get('fileName').strip()

    service_response, service_data = ProjectService.download_models(project_name, file_name)

    if service_response == 200:
        return send_from_directory(directory=service_data[0], path=service_data[1], as_attachment=True)
    else:
        try_response_error_codes(service_response)
    

@app.route('/createProject', methods=['POST'])
def create_project():
    project_name = request.form.get("project_name")
    
    service_response, service_data = ProjectService.create_project_unique(project_name)

    if service_response == 201:
        data = {'message': 'Project created', 'code': 'SUCCESS'}
        return make_response(jsonify(data), 201)
    else:
        try_response_error_codes(service_response)


@app.route('/editProjectName', methods=['POST'])
def edit_project_name():
    old_name = request.form.get("oldProjectName")
    new_name = request.form.get("newProjectName")
    
    service_response, service_data = ProjectService.edit_project_name(old_name, new_name)

    if service_response == 200:
        data = {'message': 'Project name updated', 'code': 'SUCCESS'}
        return make_response(jsonify(data), 200)
    else:
        try_response_error_codes(service_response)


@app.route('/duplicate_project', methods=['POST'])
def duplicate_project():
    old_name = request.form.get("project_name")
    new_name = old_name+" -copy"
    
    service_response, service_data = ProjectService.duplicate_project(old_name, new_name)

    if service_response == 201:
        data = {'message': 'Project duplicated successfully', 'code': 'SUCCESS'}
        return make_response(jsonify(data), 201)
    else:
        try_response_error_codes(service_response)


@app.route('/deleteProject', methods=['DELETE'])
def delete_project():
    project_name = request.form.get("project_name")
    
    service_response, service_data = ProjectService.delete_project(project_name)
    
    if service_response == 200:
        data = {'message': 'Project deleted successfully', 'code': 'SUCCESS'}
        return make_response(jsonify(data), 200)
    else:
        try_response_error_codes(service_response)


@app.route('/getAllProjects', methods=['GET'])
def get_all_projects():
    
    service_response, service_data = ProjectService.get_all_projects()

    if service_response == 200:
        data = {'projects': service_data, 'code': 'SUCCESS'}
        return make_response(jsonify(data), 201)
    else:
        try_response_error_codes(service_response)

   
@app.route('/generate_iframe', methods=['GET'])
def generate_iframe():
    project_name = request.args.get('project_name').strip()

    service_response, service_data = tools.generate_iframe(project_name)

    if service_response == 200:
        return make_response(jsonify({'iframe_code': service_data, 'message': 'Iframe generated successfully', 'code': 'SUCCESS'}), 200)
    else:
        try_response_error_codes(service_response)

    
@app.route("/login", methods=["GET","POST"])
def login():
    name = request.form.get("username")
    password = request.form.get("password")   

    if not session.get('logged_in_id') :
        session['logged_in_id'] = ""

    g = session['logged_in_id']
    
    service_response, service_data = account_service.try_login(g, name, password)

    if service_response == 201:
        data = {'message': 'Logged in sucessfuly', 'code': 'SUCCESS'}
        return make_response(jsonify(data), 201)
    else:
        try_response_error_codes(service_response)


@app.route("/register", methods=["GET", "POST"])
def register():
    name = request.form.get("username")
    password = request.form.get("password")

    service_response, service_data = account_service.try_register(name, password)

    if service_response == 201:
        data = {'message': 'Registered sucessfuly', 'code': 'SUCCESS'}
        return make_response(jsonify(data), 201)
    else:
        try_response_error_codes(service_response)
   

def try_response_error_codes(service_response):
    if service_response == 404:
        return abort(404, description=config["server_responses"]["not_found"])
    elif service_response == 409:
        return abort(409, description=config["server_responses"]["conflict"])
    elif service_response == 500:
        return abort(500, description=config["server_responses"]["server_error_message"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)