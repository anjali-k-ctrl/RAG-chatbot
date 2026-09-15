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
 MongoDB Atlas
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
- MongoDB Atlas metadata management
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
| Database | MongoDB Atlas |
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

### 2. Install Dependencies

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file:

```env
MONGODB_URI=
MONGODB_DATABASE=

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
AWS_BUCKET_NAME=

OPENSEARCH_HOST=
OPENSEARCH_PORT=443

GEMINI_API_KEY=

FRONTEND_URL=http://localhost:5500
```

> **Never commit `.env` or real credentials to GitHub.**

### 4. Run the Backend

```bash
uvicorn app:app --reload
```

API: `http://localhost:8000`

Swagger: `http://localhost:8000/docs`

### 5. Run the Frontend

```bash
python -m http.server 5500 --directory frontend
```

Frontend: `http://localhost:5500`

## Buyer / Seller Isolation

Documents are assigned an audience during upload:

- `buyer`
- `seller`

The selected audience is stored with the document metadata and used as a filter during OpenSearch retrieval. This ensures that Buyer questions retrieve Buyer documentation and Seller questions retrieve Seller documentation.

## Knowledge Gap Tracking

Questions that cannot be answered from the available documentation can be recorded as knowledge gaps.

The system tracks:

- Question
- Audience
- Page name
- Occurrence count
- Status
- Resolution information

When new documentation is uploaded, pending questions for the same audience can be checked against the new knowledge.

## Database

MongoDB Atlas stores application metadata and operational records, including:

- Documents
- Unanswered questions
- User feedback
- System health logs
- Failed retrieval requests
- Irrelevant questions
- Chatbot settings

Amazon OpenSearch stores document chunks and embeddings for retrieval, while AWS S3 stores the original documents.
