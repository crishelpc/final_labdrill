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

@app.route("/patients", methods=["POST"])
def add_patient():
    data = request.get_json()
    error_message, status_code = validate_patient_input(data)
    if error_message:
        return jsonify({"error": error_message}), status_code

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO Patients (patientFirstName, patientLastName, patientHomePhone, patientEmailAddress) VALUES (%s, %s, %s, %s)",
            (data['patientFirstName'], data['patientLastName'], data['patientHomePhone'], data['patientEmailAddress'])
        )
        mysql.connection.commit()
        cursor.close()
        return jsonify(
            {
                "message": "Patient added successfully"
            }
        ), HTTPStatus.CREATED
    
    except Exception as e:
        return jsonify(
            {
                "error": str(e)
            }
        ), HTTPStatus.BAD_REQUEST

@app.route("/patientadmissions", methods=["POST"])
def add_admission():
    info = request.get_json()
    error_message, status_code = validate_admission_input(info)
    if error_message:
        return jsonify(
            {
                "error": error_message
            }
        ), status_code

    try:
        cur = mysql.connection.cursor()
        cur.execute(
            """INSERT INTO PatientAdmissions (patientID, dateOfAdmission, dateOfDischarge)
            VALUES (%s, %s, %s)""",
            (info["patientID"], info["dateOfAdmission"], info["dateOfDischarge"])
        )
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()
        return jsonify(
            {
                "message": "Admission added successfully", "rows_affected": rows_affected
            }
        ), HTTPStatus.CREATED
    
    except Exception as e:
        return jsonify(
            {"error": str(e)
            }
        ), HTTPStatus.BAD_REQUEST

@app.route("/treatments", methods=["POST"])
def add_treatment():
    info = request.get_json()
    error_message, status_code = validate_treatment_input(info)
    if error_message:
        return jsonify(
            {
                "error": error_message
            }
        ), status_code

    try:
        cur = mysql.connection.cursor()
        cur.execute(
            """INSERT INTO Treatments (staffID, patientID, treatmentDescription, treatmentStatus)
            VALUES (%s, %s, %s, %s)""",
            (info['staffID'], info["patientID"], info["treatmentDescription"], info["treatmentStatus"])
        )
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()
        return jsonify(
            {
                "message": "Treatment of patient added successfully", "rows_affected": rows_affected
            }
        ), HTTPStatus.CREATED
    
    except Exception as e:
        return jsonify(
            {
                "error": str(e)
            }
        ), HTTPStatus.BAD_REQUEST
    

@app.route("/treatments/<int:treatment_id>", methods=["PUT"])
def update_treatment(treatment_id):
    info = request.get_json()
    treatmentStatus = info.get("treatmentStatus")
    if not treatmentStatus:
        return jsonify(
            {
                "error": "'treatmentStatus' is required"
            }
            ), HTTPStatus.BAD_REQUEST

    try:
        cur = mysql.connection.cursor()
        cur.execute(
            """UPDATE Treatments SET treatmentStatus = %s WHERE treatmentID = %s""",
            (treatmentStatus, treatment_id),
        )
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()
        return jsonify(
            {
                "message": "Patient treatment status updated successfully", "rows_affected": rows_affected
            }
        ), HTTPStatus.OK
    
    except Exception as e:
        return jsonify(
            {
                "error": str(e)
            }
        ), HTTPStatus.BAD_REQUEST
    
@app.route('/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""DELETE FROM Patients WHERE patientID = %s""", (patient_id,))
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()
        return jsonify(
            {
                "message": "Patient record deleted successfully", "rows_affected": rows_affected
            }
        ), HTTPStatus.OK
    
    except Exception as e:
        return jsonify(
            {
                "error": str(e)
            }
        ), HTTPStatus.BAD_REQUEST

@app.route('/treatments/<int:treatment_id>', methods=['DELETE'])
def delete_treatment(treatment_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""DELETE FROM Treatments WHERE treatmentID = %s""", (treatment_id,))
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()
        return jsonify(
            {
                "message": "Treatment record deleted successfully", "rows_affected": rows_affected
            }
        ), HTTPStatus.OK
    
    except Exception as e:
        return jsonify(
            {
                "error": str(e)
            }
        ), HTTPStatus.BAD_REQUEST


if __name__ == "__main__":
    app.run(debug=True)