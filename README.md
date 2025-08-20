# rfp_automation

Automating RFP generation using AI agents.

## Getting started

## Getting Started

### Backend

1. **Navigate to the backend directory:**
   ```
   cd backend
   ```

2. **Set up environment variables**  
   Create a `.env` file in `backend/` with:
   ```
   AZURE_OPENAI_KEY=your-azure-openai-key
   AZURE_OPENAI_ENDPOINT=your-azure-endpoint-url
   AZURE_SQL_CONNECTION_STRING=your-azure-sql-endpoint
   ```

3. **Install backend dependencies:**
   (Highly recommended to create a venv to avoid package issues)
   ```
   pip install -r requirements.txt
   ```

5. **(Optional) Add PPTX template:**  
   Place `cover_page.pptx` into `/app/templates/` if you want to generate PowerPoint files.

6. **(Optional) Add knowledge documents:**  
   Place relevant PDF or PPTX files into `/knowledge/` to provide context for answer generation.

7. **Run the backend:**
   ```
   python main.py
   ```
   This starts a FastAPI server on port 8000.

### Frontend

1. **Navigate to the frontend directory:**
   ```
   cd frontend
   ```

2. **Install frontend dependencies:**
   ```
   npm install
   ```

3. **Start the frontend development server:**
   ```
   npm run dev
   ```
   The app will run locally and communicate with the backend on `http://127.0.0.1:8000`.
