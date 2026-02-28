from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest, MenuRequest
from services.qa_service import QAService

router = APIRouter()
service = QAService()


@router.post("/chat")
def chat_endpoint(req: ChatRequest):
    if req.mode == "guided":
        return service.handle_guided(req.option)

    if req.mode == "ask":
        answer = service.handle_question(req.question)
        # pydantic model already constructed in service
        return answer.dict() if hasattr(answer, "dict") else answer

    raise HTTPException(status_code=400, detail="Invalid mode")


@router.get("/menu")
def menu():
    return {"menu": service.get_menu()}


@router.post("/reload")
def reload_knowledge_base():
    """Reload the knowledge base from local documents."""
    try:
        service.pipeline.ingest_documents_from_folder("data")
        return {"status": "success", "message": "Knowledge base reloaded from local documents"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
