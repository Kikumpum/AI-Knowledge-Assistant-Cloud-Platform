from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.api.dependencies import CurrentUser, DbSession
from app.api.schemas import DocumentResponse
from app.application.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("", response_model=list[DocumentResponse])
async def list_documents(current_user: CurrentUser, db: DbSession):
    service = DocumentService(db)
    return await service.list_documents(current_user.id)


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    current_user: CurrentUser,
    db: DbSession,
    file: UploadFile = File(...),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")
    content = await file.read()
    service = DocumentService(db)
    try:
        doc = await service.save_upload(current_user, file.filename, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to process document")
    return doc


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: int,
    current_user: CurrentUser,
    db: DbSession,
):
    service = DocumentService(db)
    ok = await service.delete_document(current_user, document_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Document not found")
