from flask import Flask, render_template, request, session, flash, redirect, url_for, get_flashed_messages, jsonify, abort, make_response, send_file, send_from_directory, abort, jsonify
import os
import zipfile
import io
from fileinput import filename 

app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route("/")
def home():
    return render_template("main.html")

@app.route('/upload', methods=['POST'])
def upload():
    received_data = request.form['myData']
    file_path = os.path.join(os.path.dirname(__file__), 'project', 'saveData.txt')
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
def download():
    file_path = os.path.join(os.path.dirname(__file__), 'project', 'saveData.txt')
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        abort(404, description="File not found")

@app.route("/downloadModels")
def downloadModels():
    models_folder = os.path.join(os.path.dirname(__file__), 'project', 'models')
    
    if not os.path.exists(models_folder):
        abort(404, description="Models folder not found")
    
    memory_file = io.BytesIO()
    
    with zipfile.ZipFile(memory_file, 'w') as zip_file:
        for root, dirs, files in os.walk(models_folder):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, os.path.relpath(file_path, models_folder))
    
    memory_file.seek(0)
    
    return send_file(memory_file, mimetype='application/zip', as_attachment=True, attachment_filename='models.zip')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)