
import uuid
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel, Field
from services.deal.deal_chat_service import answer_deal_question
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from database.mongo_helpers import get_deal_proposals_collection
from services.deal.document_extractor import extract_document_text
from services.deal.deal_analysis_service import analyze_proposal

router = APIRouter(prefix="/deal", tags=["Deal Assistant"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads" / "deals"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
class DealChatRequest(BaseModel):
    proposal_id: str
    question: str
    history: list[dict] = Field(default_factory=list)

@router.post("/upload")
async def upload_proposal(
    file: UploadFile = File(...),
    audience: str = Form(...)
):
    # Validate audience
    if audience not in ["buyer", "seller"]:
        raise HTTPException(
            status_code=400,
            detail="Audience must be buyer or seller."
        )

    # Validate filename and extension
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is missing."
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in [".pdf", ".docx"]:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported."
        )

    # Read file with size limit
    file_bytes = await file.read(MAX_FILE_SIZE + 1)

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size must not exceed 10 MB."
        )

    # Basic file signature validation
    if extension == ".pdf" and not file_bytes.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file."
        )

    if extension == ".docx" and not file_bytes.startswith(b"PK"):
        raise HTTPException(
            status_code=400,
            detail="Invalid DOCX file."
        )

    # Extract document text
    try:
        extracted_text = extract_document_text(
            file_bytes,
            file.filename
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not read document: {str(e)}"
        )

    # Generate unique proposal ID
    proposal_id = str(uuid.uuid4())

    # Save original file separately
    saved_path = UPLOAD_DIR / f"{proposal_id}{extension}"

    try:
        saved_path.write_bytes(file_bytes)

        # Save proposal metadata in MongoDB
        collection = get_deal_proposals_collection()

        collection.insert_one({
            "proposal_id": proposal_id,
            "filename": Path(file.filename).name,
            "file_path": str(saved_path),
            "audience": audience,
            "status": "uploaded",
            "extracted_text": extracted_text,
            "created_at": datetime.utcnow()
        })

    except Exception:
        saved_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail="Could not save proposal."
        )

    return {
        "success": True,
        "proposal_id": proposal_id,
        "filename": Path(file.filename).name,
        "audience": audience,
        "status": "uploaded",
        "extracted_characters": len(extracted_text),
        "message": "Proposal uploaded and text extracted successfully."
    }

@router.post("/analyze/{proposal_id}")
async def analyze_uploaded_proposal(proposal_id: str):

    collection = get_deal_proposals_collection()

    # Find uploaded proposal
    proposal = collection.find_one({
        "proposal_id": proposal_id
    })

    if not proposal:
        raise HTTPException(
            status_code=404,
            detail="Proposal not found."
        )

    if proposal.get("status") == "analyzed":
        return {
            "success": True,
            "proposal_id": proposal_id,
            "analysis": proposal.get("analysis"),
            "message": "Proposal already analyzed."
        }

    extracted_text = proposal.get("extracted_text", "")

    if not extracted_text:
        raise HTTPException(
            status_code=400,
            detail="No extracted text available."
        )

    # Update processing status
    collection.update_one(
        {"proposal_id": proposal_id},
        {"$set": {"status": "analyzing"}}
    )

    try:
        analysis = analyze_proposal(extracted_text)

        collection.update_one(
            {"proposal_id": proposal_id},
            {
                "$set": {
                    "status": "analyzed",
                    "analysis": analysis
                }
            }
        )

        return {
            "success": True,
            "proposal_id": proposal_id,
            "analysis": analysis,
            "message": "Proposal analyzed successfully."
        }

    except Exception as e:

        collection.update_one(
            {"proposal_id": proposal_id},
            {"$set": {"status": "analysis_failed"}}
        )

        raise HTTPException(
            status_code=500,
            detail=f"Proposal analysis failed: {str(e)}"
        )

@router.post("/chat")
async def deal_chat(request: DealChatRequest):

    collection = get_deal_proposals_collection()

    proposal = collection.find_one({
        "proposal_id": request.proposal_id
    })

    if not proposal:
        raise HTTPException(
            status_code=404,
            detail="Proposal not found."
        )

    if proposal.get("status") != "analyzed":
        raise HTTPException(
            status_code=400,
            detail="Please analyze the proposal before asking questions."
        )

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:
        answer = answer_deal_question(
            question=request.question,
            extracted_text=proposal.get("extracted_text", ""),
            analysis=proposal.get("analysis", {}),
            history=request.history
        )

        return {
            "success": True,
            "proposal_id": request.proposal_id,
            "answer": answer
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not answer question: {str(e)}"
        )
