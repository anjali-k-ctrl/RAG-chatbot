# MediaShippers RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot for answering questions about the MediaShippers platform using internal documentation.

## Architecture

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
Document Ingestion
Document Upload
   ↓
AWS S3
   ↓
PostgreSQL (Metadata)
   ↓
Text Extraction → Chunking → Embeddings
   ↓
Amazon OpenSearch
Key Features
RAG-based question answering
Buyer/Seller documentation separation
AWS S3 document storage
PostgreSQL metadata management
Amazon OpenSearch vector search
Gemini-powered responses
Document upload and deletion
User feedback
Unanswered-question and knowledge-gap tracking
Health and retrieval monitoring
Admin and analytics endpoints
Tech Stack
Backend: Python, FastAPI
Database: PostgreSQL
Storage: AWS S3
Vector Search: Amazon OpenSearch
LLM: Google Gemini
Frontend: HTML, CSS, JavaScript
Setup
1. Clone
git clone https://github.com/anjali-k-ctrl/RAG-chatbot.git
cd RAG-chatbot
2. Install dependencies
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
3. Configure environment variables

Create a .env file with the required PostgreSQL, AWS, OpenSearch, and Gemini configuration.

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


4. Run
uvicorn app:app --reload

API: http://localhost:8000

Swagger: http://localhost:8000/docs

Buyer / Seller Isolation

Documents are assigned an audience (buyer or seller) during upload.

The selected audience is applied as a filter during OpenSearch retrieval, ensuring that responses are generated from the relevant documentation.
