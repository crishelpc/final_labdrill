# final_labdrill

# Hospice Patient Care 

## Description
This is a Conceptual Data Model for a Hospice Care System. It helps manage patient information, medical conditions, treatments, staff details to make care easier and more organized.

## Installation
```cmd
pip install -r requirements.txt
```
## Configuration
Environment variables needed:

DATABASE_URL
SECRET_KEY

## API Endpoints (markdown table)
| Endpoint                                      | Method   | Description                                                               |
|-----------------------------------------------|----------|---------------------------------------------------------------------------|
| `/`                                           | `GET`    | Returns a welcome message.                                                |
| `/patients`                                   | `GET`    | Retrieves all patients.                                                   |
| `/patients`                                   | `POST`   | Adds a new patient.                                                       |
| `/patientadmissions/<int:patient_id>`         | `GET`    | Retrieves patient admission details for a specific patient ID.            |
| `/patientadmissions`                          | `POST`   | Adds a new admission record for a patient.                                |
| `/healthprofessionals/<int:staff_id>/patients`| `GET`    | Retrieves all patients treated by a specific health professional.         |
| `/treatments/<int:patient_id>`                | `GET`    | Retrieves treatment history for a specific patient.                       |
| `/treatments`                                 | `POST`   | Adds a treatment record for a patient.                                    |
| `/treatments/<int:treatment_id>`              | `PUT`    | Updates the status of a specific treatment.                               |
| `/patients/<int:patient_id>`                  | `DELETE` | Deletes a specific patient record.                                        |
| `/treatments/<int:treatment_id>`              | `DELETE` | Deletes a specific treatment record.                                      |

## Testing
 Instructions for running tests
…

## Git Commit Guidelines

Use conventional commits:
```bash
feat: add user authentication
fix: resolve database connection issue
docs: update API documentation
test: add user registration tests

