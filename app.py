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

@app.route("/")
def index_page():
    return jsonify({"message": "WELCOME TO HOSPICE PATIENT CARE!"}), HTTPStatus.OK

def validate_patient_input(data):
    required_fields = ['patientFirstName', 'patientLastName', 'patientHomePhone', 'patientEmailAddress']
    for field in required_fields:
        if field not in data or not data[field]:
            return f"'{field}' is required", HTTPStatus.BAD_REQUEST
    return None, None

def validate_admission_input(data):
    required_fields = ['patientID', 'dateOfAdmission', 'dateOfDischarge']
    for field in required_fields:
        if field not in data or not data[field]:
            return f"'{field}' is required", HTTPStatus.BAD_REQUEST
    try:
        datetime.strptime(data["dateOfAdmission"], "%Y-%m-%d")
        datetime.strptime(data["dateOfDischarge"], "%Y-%m-%d")
    except ValueError:
        return "'dateOfAdmission' and 'dateOfDischarge' must be in 'YYYY-MM-DD' format", HTTPStatus.BAD_REQUEST
    return None, None

def validate_treatment_input(data):
    required_fields = ['staffID', 'patientID', 'treatmentDescription', 'treatmentStatus']
    for field in required_fields:
        if field not in data or not data[field]:
            return f"'{field}' is required", HTTPStatus.BAD_REQUEST
    return None, None

def data_fetch(query, params=None):
    cur = mysql.connection.cursor()
    cur.execute(query, params)
    result = cur.fetchall()
    cur.close()
    return result

@app.route("/patients", methods=["GET"])
def get_patients():
    data = data_fetch("""SELECT * FROM patients""")
    return jsonify(data), HTTPStatus.OK

@app.route("/patientadmissions/<int:patient_id>", methods=["GET"])
def get_patient_admission(patient_id):
    data = data_fetch("""SELECT * FROM PatientAdmissions WHERE patientID = %s""", (patient_id,))
    if not data:
        return jsonify(
            {
                "error": "Admission not found for the given patient"
            }), HTTPStatus.NOT_FOUND
    
    return jsonify(data), HTTPStatus.OK

@app.route("/healthprofessionals/<int:staff_id>/patients", methods=["GET"])
def get_patients_info(staff_id):
    data = data_fetch("""
        SELECT DISTINCT Patients.patientID, Patients.patientFirstName, Patients.patientLastName, 
                        Patients.patientHomePhone, Patients.patientEmailAddress
        FROM Treatments
        JOIN Patients ON Treatments.patientID = Patients.patientID
        WHERE Treatments.staffID = %s
    """, (staff_id,))

    if not data:
        return jsonify(
            {
                "error": "No patients found for this health professional"
            }
        ), HTTPStatus.NOT_FOUND

    return jsonify(data), HTTPStatus.OK

@app.route("/treatments/<int:patient_id>", methods=["GET"])
def get_treatment_history(patient_id):
    data = data_fetch("""SELECT treatmentID, treatmentDescription, treatmentStatus
        FROM Treatments WHERE patientID = %s""", (patient_id,))
    return jsonify(data), HTTPStatus.OK

if __name__ == "__main__":
    app.run(debug=True)