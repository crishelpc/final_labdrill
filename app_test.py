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
