# KBTCOE NotesDesk — Frontend + Flask Backend + SQLite

This version converts the uploaded single-file frontend into a local full-stack project.

## Stack
- Frontend: HTML, CSS, JavaScript (original uploaded UI)
- Backend: Python Flask
- Database: SQLite
- File storage: `uploads/`

## Run on Windows
```powershell
cd KBTCOE_NotesDesk
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python backend\app.py
```
Open: http://127.0.0.1:5000

## Database
The SQLite database is created automatically at:
`database/notesdesk.db`

## Important
The original frontend used Google Apps Script and Cashfree. This local version replaces the Google Apps Script URL with `/api` and stores users/materials/orders in SQLite. The payment endpoint is a **local demo flow**, not a real payment gateway. For real Cashfree payments, Cashfree server credentials and webhook verification must be added on the backend.
