from flask import Flask, request, session, render_template, make_response, jsonify, url_for, send_file, send_from_directory, abort, g
import os
from dotenv import load_dotenv
import tomli
from flask_cors import CORS, cross_origin
from services.project_service import ProjectService
from services.account_service import AccountService
from services.logger_service import LoggerService
from tools import tools
from repository.mongo_repository import MongoRepository

app = Flask(__name__)
# CORS configuration - allow web test client and Unity client
CORS(app,
     origins=[
         "http://localhost:5000",      # Web test client
         "http://localhost:5001",      # Unity client
         "http://localhost:8050",      # Docker Web test client
         "http://127.0.0.1:5000",      # Web test client
         "http://127.0.0.1:5001",      # Unity client
         "http://127.0.0.1:8050",      # Docker Web test client¨
         "172.19.0.1",                 # Deployment host internal IP
         "https://dtwin.rqa.cz/",      # Deployment
     ],
     supports_credentials=True)
load_dotenv(dotenv_path="../../.env.production")
app.secret_key = os.getenv("SECRET_KEY")

config_path = os.path.join(os.path.dirname(__file__), "../conf.toml")
with open(config_path, "rb") as file:
    config = tomli.load(file)


# Configure logging through LoggerService
LoggerService.configure_app_logger(app)
LoggerService.log_startup_info()

app.before_request(LoggerService.create_request_logger())
app.after_request(LoggerService.create_response_logger())

repo = MongoRepository(uri=os.getenv("MONGO_URI"), database_name=config["database"]["database_name"])
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
    asset_hash = request.form.get("asset_hash")

    service_response, service_data = ProjectService.upload_model(project_name, asset_hash, request.files)

    if service_response == 201:
        data = {'message': config["server_responses"]["success"], 'code': 'SUCCESS'}
        return make_response(jsonify(data), 201)
    else:
        try_response_error_codes(service_response)


@app.route("/download")
def download():
    project_name = request.args.get('project_name').strip()

    service_response, service_data = ProjectService.download_data(project_name)

    if service_response == 200:
        data = service_data
        return make_response(data, 200)
    else:
        try_response_error_codes(service_response)

@app.route("/downloadModels")
def downloadModels():
    project_name = request.args.get('project_name').strip()
    asset_hash = request.args.get('asset_hash').strip()
    file_name = request.args.get('file_name').strip()

    service_response, service_data = ProjectService.download_models(
        project_name, asset_hash, file_name
    )

    if service_response == 200:
        return send_from_directory(
            directory=service_data[0],
            path=service_data[1],
            as_attachment=True
        )
    else:
        try_response_error_codes(service_response)


@app.route('/list_model_files', methods=['GET'])
@cross_origin(origin='http://127.0.0.1:5001')
def list_model_files():
    project_name = request.args.get("project_name")
    asset_hash = request.args.get("asset_hash")

    if not project_name or not asset_hash:
        return make_response({"message": "Missing parameters"}, 400)

    try:
        project = ProjectService.create_new_project(project_name)
        asset_dir = os.path.join(project.models_dir, asset_hash)

        if not os.path.exists(asset_dir):
            return make_response({"message": "Asset not found"}, 404)

        files = [
            f for f in os.listdir(asset_dir)
            if os.path.isfile(os.path.join(asset_dir, f))
        ]

        return jsonify({ "items": files }), 200

    except Exception as e:
        print(e)
        return make_response({"message": "Server error"}, 500)



@app.route('/createProject', methods=['POST'])
def create_project():
    project_name = request.form.get("project_name")
    project_id = request.form.get('project_id')

    service_response, service_data = ProjectService.create_project_with_data(project_name, project_id)

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
    LoggerService.info(f"Get all projects response code: {service_response}")
    LoggerService.info(f"Get all projects data: {service_data}")

    if service_response == 200:
        print("SENDING DATA: ", service_data)
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
    LoggerService.info(f"Login attempt for user: {name}")

    service_response, service_data = account_service.try_login(g, name, password)
    LoggerService.info(f"Login response code: {service_response}")

    if service_response == 201:
        data = {'message': 'Logged in sucessfuly', 'code': 'SUCCESS'}
        return make_response(jsonify(data), 201)
    else:
        return try_response_error_codes(service_response)


@app.route("/register", methods=["GET", "POST"])
def register():
    name = request.form.get("username")
    password = request.form.get("password")
    LoggerService.info(f"Register attempt for user: {name}")

    service_response, service_data = account_service.try_register(name, password)
    LoggerService.info(f"Register response code: {service_response}")

    if service_response == 201:
        data = {'message': 'Registered sucessfuly', 'code': 'SUCCESS'}
        return make_response(jsonify(data), 201)
    else:
        return try_response_error_codes(service_response)


def try_response_error_codes(service_response):
    if service_response == 401:
        return abort(401, description="Unauthorized - Invalid credentials")
    elif service_response == 404:
        return abort(404, description=config["server_responses"]["not_found"])
    elif service_response == 409:
        return abort(409, description=config["server_responses"]["conflict"])
    elif service_response == 500:
        return abort(500, description=config["server_responses"]["server_error_message"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)