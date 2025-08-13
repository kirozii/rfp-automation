# rfp_automation

Automating RFP generation using AI agents.

## Getting started

### Backend

Navigate to /backend.

Set the variables AZURE_OPENAI_KEY and AZURE_OPENAI_ENDPOINT in backend/.env

Run `pip install -r requirements.txt` to install backend dependencies.

Add cover_page.pptx to /app/templates. (not required if youre not generating ppts)

Populate /knowledge with any relevant knowledge documents (PDF, PPTX)

Now run `py main.py` in /backend to run the backend.

### Frontend

Navigate to /frontend.

Run `npm install` to install frontend dependencies.

Now run `npm run dev` to run the frontend.
