from flask import Flask, render_template, request, session, flash, redirect, url_for, get_flashed_messages, jsonify

app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route("/")
def home():
    return render_template("main.html")

@app.route('/upload', methods=['POST'])
def upload():
    received_data = request.form['myData']
    return "Byla nám poslána data" + received_data

@app.route("/download")
def download():
    return "Posíláme data"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)