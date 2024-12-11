import pytest
from app import app  


@pytest.fixture
def mock_db(mocker):
    mock_conn = mocker.patch('flask_mysqldb.MySQL.connection')
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_cursor

# General Tests
def test_index_page():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b"WELCOME TO HOSPICE PATIENT CARE!" in response.data

# Patients Tests
def test_get_patients_empty(mock_db):
    mock_db.fetchall.return_value = []
    client = app.test_client()
    response = client.get('/patients')
    assert response.status_code == 200
    assert response.json == []

def test_get_patients(mock_db):
    mock_db.fetchall.return_value = [
        {
            "patientID": 1,
            "patientFirstName": "John",
            "patientLastName": "Doe",
            "patientHomePhone": "123456789",
            "patientEmailAddress": "john@example.com",
        }
    ]
    client = app.test_client()
    response = client.get('/patients')
    assert response.status_code == 200
    assert response.json[0]['patientFirstName'] == "John"

def test_add_patient_missing_fields(mock_db):
    client = app.test_client()
    response = client.post('/patients', json={})
    assert response.status_code == 400
    assert b"'patientFirstName' is required" in response.data

def test_add_patient_success(mock_db):
    mock_db.rowcount = 1
    client = app.test_client()
    response = client.post(
        '/patients',
        json={
            "patientFirstName": "John",
            "patientLastName": "Doe",
            "patientHomePhone": "123456789",
            "patientEmailAddress": "john@example.com",
        },
    )
    assert response.status_code == 201
    assert b"Patient added successfully" in response.data

# Patient Admissions Tests
def test_get_patient_admission_not_found(mock_db):
    mock_db.fetchall.return_value = []
    client = app.test_client()
    response = client.get('/patientadmissions/999')
    assert response.status_code == 404
    assert b"Admission not found for the given patient" in response.data

def test_get_patient_admission_success(mock_db):
    mock_db.fetchall.return_value = [
        {
            "admissionID": 1,
            "patientID": 1,
            "dateOfAdmission": "2024-01-01",
            "dateOfDischarge": "2024-01-10",
        }
    ]
    client = app.test_client()
    response = client.get('/patientadmissions/1')
    assert response.status_code == 200
    assert response.json[0]['dateOfAdmission'] == "2024-01-01"

# Treatments Tests
def test_get_treatment_history_empty(mock_db):
    mock_db.fetchall.return_value = []
    client = app.test_client()
    response = client.get('/treatments/999')
    assert response.status_code == 200
    assert response.json == []

def test_get_treatment_history_success(mock_db):
    mock_db.fetchall.return_value = [
        {
            "treatmentID": 1,
            "treatmentDescription": "Physical Therapy",
            "treatmentStatus": "Completed",
        }
    ]
    client = app.test_client()
    response = client.get('/treatments/1')
    assert response.status_code == 200
    assert response.json[0]['treatmentDescription'] == "Physical Therapy"

def test_add_treatment_missing_fields(mock_db):
    client = app.test_client()
    response = client.post('/treatments', json={})
    assert response.status_code == 400
    assert b"'staffID' is required" in response.data

def test_add_treatment_success(mock_db):
    mock_db.rowcount = 1
    client = app.test_client()
    response = client.post(
        '/treatments',
        json={
            "staffID": 1,
            "patientID": 1,
            "treatmentDescription": "Physical Therapy",
            "treatmentStatus": "In Progress",
        },
    )
    assert response.status_code == 201
    assert b"Treatment of patient added successfully" in response.data

def test_update_treatment_missing_status(mock_db):
    client = app.test_client()
    response = client.put('/treatments/1', json={})
    assert response.status_code == 400
    assert b"'treatmentStatus' is required" in response.data

def test_update_treatment_success(mock_db):
    mock_db.rowcount = 1
    client = app.test_client()
    response = client.put('/treatments/1', json={"treatmentStatus": "Completed"})
    assert response.status_code == 200
    assert b"Patient treatment status updated successfully" in response.data

#Health professional
def test_get_patient_info_not_found(mock_db):
    mock_db.fetchall.return_value = []
    client = app.test_client()
    response = client.get('/healthprofessionals/999/patients')
    assert response.status_code == 404
    assert b"No patients found for this health professional" in response.data

def test_get_patient_info_success(mock_db):
    mock_db.fetchall.return_value = [
        {
            "patientID": 1,
            "patientFirstName": "Aitor",
            "patientLastName": "Reina",
            "patientHomePhone": "(361) 548-9276",
            "patientEmailAddress": "esarabia@gmail.com",
        }
    ]
    client = app.test_client()
    response = client.get('/healthprofessionals/1/patients')
    assert response.status_code == 200
    assert response.json[0]["patientFirstName"] == "Aitor"

# Deletion Tests
def test_delete_patient_success(mock_db):
    mock_db.rowcount = 1
    client = app.test_client()
    response = client.delete('/patients/1')
    assert response.status_code == 200
    assert b"Patient record deleted successfully" in response.data

def test_delete_treatment_success(mock_db):
    mock_db.rowcount = 1
    client = app.test_client()
    response = client.delete('/treatments/1')
    assert response.status_code == 200
    assert b"Treatment record deleted successfully" in response.data