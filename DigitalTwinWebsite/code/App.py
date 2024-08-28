from flask import Flask, render_template, request, session, flash, redirect, url_for, get_flashed_messages, jsonify, abort, make_response, send_file, send_from_directory, abort, jsonify
import os
import zipfile
import io
from fileinput import filename 
from flask_cors import CORS, cross_origin

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

@app.route("/")
def home():
    return render_template("main.html")

@app.route('/upload', methods=['POST'])
def upload():
    received_data = request.form['myData']
    save_dir = os.path.join(os.path.dirname(__file__), 'project')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    file_path = os.path.join(save_dir, 'saveData.txt')
    with open(file_path, 'w') as file:
        file.write(received_data)
    data = {'message': 'Done', 'code': 'SUCCESS'}
    return make_response(jsonify(data), 201)

@app.route('/uploadFiles', methods=['POST'])
def uploadFiles():
    if request.method == 'POST':
        f = request.files['file'] 
        save_path = os.path.join(os.path.dirname(__file__), 'project', 'models')
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        file_path = os.path.join(save_path, f.filename)
        f.save(file_path)
        data = {'message': 'Done', 'code': 'SUCCESS'}
        return make_response(jsonify(data), 201)

@app.route("/download")
@cross_origin(origin='http://127.0.0.1:5001')
def download():
    file_path = os.path.join(os.path.dirname(__file__), 'project', 'saveData.txt')
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        abort(404, description="File not found")

@app.route("/downloadModels")
@cross_origin(origin='http://127.0.0.1:5001')
def downloadModels():
    models_folder = os.path.join(os.path.dirname(__file__), 'project', 'models')
    file_name = request.args.get('fileName')
    if not file_name:
        abort(400, description="File name not provided")
    file_path = os.path.join(models_folder, file_name)
    if not os.path.exists(file_path):
        abort(404, description="File not found")
    return send_from_directory(models_folder, file_name, as_attachment=True)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)