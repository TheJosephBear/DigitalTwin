from flask import Flask, request, session, jsonify, make_response, send_file, abort
from flask_cors import CORS
from DigitalTwinWebsite.config import Config
from DigitalTwinWebsite.services.account_service import AccountService
from DigitalTwinWebsite.services.project_service import ProjectService
from DigitalTwinWebsite.models.user_model import db as user_db
from DigitalTwinWebsite.models.project_model import db as project_db

app = Flask(__name__)
app.config.from_object(Config)
user_db.init_app(app)  # Initialize Flask-MongoEngine for User
project_db.init_app(app)  # Initialize Flask-MongoEngine for Project
CORS(app)
app.secret_key = Config.SECRET_KEY

account_service = AccountService()
project_service = ProjectService()


@app.route('/register', methods=['POST'])
def register():
    username = request.form.get("username")
    password = request.form.get("password")

    user = account_service.register_user(username, password)
    if user:
        return jsonify({'message': 'Registered successfully', 'code': 'SUCCESS'}), 201
    return jsonify({'message': 'User already exists', 'code': 'ERROR'}), 409


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    user = account_service.authenticate_user(username, password)
    if user:
        session['user_id'] = str(user.id)
        return jsonify({'message': 'Logged in successfully', 'code': 'SUCCESS'}), 200
    return jsonify({'message': 'Invalid credentials', 'code': 'ERROR'}), 401


@app.route('/createProject', methods=['POST'])
def create_project():
    project_name = request.form['projectName']
    project = project_service.create_project(project_name)
    if project:
        return jsonify({'message': 'Project created', 'code': 'SUCCESS'}), 201
    return jsonify({'message': 'Project already exists', 'code': 'ERROR'}), 409


@app.route('/getAllProjects', methods=['GET'])
def get_all_projects():
    projects = project_service.get_all_projects()
    return jsonify({'projects': projects, 'code': 'SUCCESS'}), 200


@app.route('/deleteProject', methods=['DELETE'])
def delete_project():
    project_name = request.form['projectName']
    if project_service.delete_project(project_name):
        return jsonify({'message': 'Project deleted', 'code': 'SUCCESS'}), 200
    return jsonify({'message': 'Project not found', 'code': 'ERROR'}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)