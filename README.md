# rfp_automation

Automating RFP generation using AI agents.

NOTE: SQL ODBC Driver 18 is required for anyone attempting to run with the connection string I have provided

## Getting started

### Backend

Navigate to /backend.

Ask me for backend/.env variables. (you can see which ones to add in backend/app/core/config.py)

Run `pip install -r requirements.txt` to install backend dependencies.

Add cover_page.pptx to /app/templates.

Now run `py main.py` in /backend to run the backend.

### Frontend

Navigate to /frontend.

Run `npm install` to install frontend dependencies.

Now run `npm run dev` to run the frontend.
