
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Header
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.future import select
from .database import AsyncSessionLocal
from .models import Document, TestCase, BugReport, User
from .schemas import DocumentCreate
from .ai_service import generate_test_cases
from .utils import text_to_pdf_bytes, testcases_to_csv_bytes
from .auth import get_current_user, create_access_token
import io, json, datetime

router = APIRouter()

@router.post("/auth/token", summary="Exchange API key for JWT access token")
async def token_exchange(x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=400, detail="x-api-key header required")
    from sqlalchemy import select
    async with AsyncSessionLocal() as session:
        q = await session.execute(select(User).where(User.api_key==x_api_key))
        user = q.scalars().first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")
        token = create_access_token({"user_id": user.id, "username": user.username})
        return {"access_token": token, "token_type": "bearer"}

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/upload", summary="Upload requirement file (text) and generate test cases")
async def upload_file(file: UploadFile = File(...), db=Depends(get_db), current_user=Depends(get_current_user)):
    content = (await file.read()).decode("utf-8", errors="ignore")
    filename = file.filename
    from sqlalchemy import insert
    async with db.begin():
        res = await db.execute(insert(Document).values(filename=filename, content=content, uploaded_at=datetime.datetime.utcnow(), user_id=current_user.get("user_id")))
        doc_id = res.inserted_primary_key[0]
    testcases = await generate_test_cases(content, max_cases=20)
    async with db.begin():
        for tc in testcases:
            await db.execute(insert(TestCase).values(
                document_id=doc_id,
                title=tc.get("title"),
                description=tc.get("description",""),
                type=tc.get("type"),
                steps=tc.get("steps"),
                expected_result=tc.get("expected_result",""),
                created_at=datetime.datetime.utcnow()
            ))
    return JSONResponse({"document_id": doc_id, "generated": len(testcases)})

@router.get("/documents/{doc_id}/testcases", summary="Get test cases for a document")
async def get_testcases(doc_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    q = await db.execute(select(TestCase).where(TestCase.document_id==doc_id))
    rows = q.scalars().all()
    out = []
    for r in rows:
        out.append({
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "type": r.type,
            "steps": r.steps,
            "expected_result": r.expected_result
        })
    return out

@router.get("/documents/{doc_id}/export/csv", summary="Export test cases as CSV")
async def export_csv(doc_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    q = await db.execute(select(TestCase).where(TestCase.document_id==doc_id))
    rows = q.scalars().all()
    tcs = []
    for r in rows:
        tcs.append({
            "id": r.id, "title": r.title, "type": r.type, "steps": r.steps, "expected_result": r.expected_result, "description": r.description
        })
    csv_bytes = testcases_to_csv_bytes(tcs)
    return StreamingResponse(io.BytesIO(csv_bytes), media_type="text/csv", headers={"Content-Disposition":"attachment; filename=testcases.csv"})

@router.get("/documents/{doc_id}/export/pdf", summary="Export test cases as PDF")
async def export_pdf(doc_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    q = await db.execute(select(TestCase).where(TestCase.document_id==doc_id))
    rows = q.scalars().all()
    lines = []
    for r in rows:
        lines.append(f"Title: {r.title}")
        lines.append(f"Type: {r.type}")
        lines.append(f"Steps: {r.steps}")
        lines.append(f"Expected: {r.expected_result}")
        lines.append('-'*40)
    pdf_bytes = text_to_pdf_bytes("Generated Test Cases", lines)
    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers={"Content-Disposition":"attachment; filename=testcases.pdf"})
