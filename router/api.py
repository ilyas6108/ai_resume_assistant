from fastapi import APIRouter, UploadFile, File
import os
from apps.upload_document import upload, ask_question
from apps.request import UploadDocument, AskQuery

router = APIRouter()

@router.post("/upload-document", response_model = UploadDocument)
async def upload_document(file:UploadFile = File(...)):
    return await upload(file)

@router.post("/ask-query")
async def ask_query(body: AskQuery):
    return await ask_question(body.dict())
