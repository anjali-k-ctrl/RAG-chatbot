# MediaShippers RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot for answering questions about the MediaShippers platform using internal documentation.

## Architecture

### Chat Flow

```text
Frontend
   ↓
FastAPI
   ↓
Audience-Aware Retrieval
   ↓
Amazon OpenSearch
   ↓
Relevant Document Chunks
   ↓
Google Gemini
   ↓
Answer
```

### Document Ingestion

```text
Document Upload
      ↓
    AWS S3
      ↓
PostgreSQL (Metadata)
      ↓
Text Extraction
      ↓
   Chunking
      ↓
  Embeddings
      ↓
Amazon OpenSearch
```

## Key Features

- RAG-based question answering
- Buyer/Seller documentation separation
- AWS S3 document storage
- PostgreSQL metadata management
- Amazon OpenSearch vector search
- Gemini-powered responses
- Document upload and deletion
- User feedback
- Knowledge-gap tracking
- Health and retrieval monitoring
- Admin and analytics endpoints

## Tech Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| Storage | AWS S3 |
| Vector Search | Amazon OpenSearch |
| LLM | Google Gemini |
| Frontend | HTML, CSS, JavaScript |

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/anjali-k-ctrl/RAG-chatbot.git
cd RAG-chatbot
```

### 2. Create Virtual Environment and Install Dependencies

**Windows PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file with the required PostgreSQL, AWS, OpenSearch, and Gemini configuration.

```env
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
DB_NAME=

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
AWS_BUCKET_NAME=

OPENSEARCH_HOST=
GEMINI_API_KEY=

FRONTEND_URL=http://localhost:5500
```

> **Never commit `.env` or real credentials to GitHub.**

### 4. Run the Backend

Open a PowerShell terminal in the project folder:

```powershell
.\venv\Scripts\Activate.ps1
uvicorn app:app --reload
```

The backend should start with:

```text
Application startup complete.
```

**API:** `http://localhost:8000`

**Swagger:** `http://localhost:8000/docs`

### 5. Run the Frontend

Open a **second PowerShell terminal** in the project folder:

```powershell
python -m http.server 5500
```

Keep both terminals running:

```text
Terminal 1 → uvicorn app:app --reload
Terminal 2 → python -m http.server 5500
```

Then open:

`http://localhost:5500/frontend/index.html`

> Open the frontend through `http://localhost:5500` rather than opening `index.html` directly with `file://`.

## Buyer / Seller Isolation

Documents are assigned an audience during upload:

- `buyer`
- `seller`

The selected audience is used as a filter during OpenSearch retrieval, ensuring that responses are generated from the relevant documentation.
