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