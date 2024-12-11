from flask import Flask, jsonify, request, make_response
from flask_mysqldb import MySQL
from http import HTTPStatus
from datetime import datetime

app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "hospice_patient_care"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


if __name__ == "__main__":
    app.run(debug=True)