from fastapi import UploadFile, File
from fastapi.responses import JSONResponse
import os
from backend.apps.rag_process import rag_split_embedding_vector_store, get_answer_from_llm_vectorstore

ALLOWED_EXTENSION = [".pdf", ".docx"]
UPLOAD_DIR =  "/app/upload_document"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def upload(file:UploadFile = File(...)):

    try:
        filename = file.filename
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSION:
            return JSONResponse(
                        status_code=400,
                        content={
                            "data": [],
                            "message": "",
                            "error": f"Invalid file type : {str(ext)}"
                        }
                    )

        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        # split document , embedding chuncks vectorstore
        result = rag_split_embedding_vector_store(ext, file_path)

        return JSONResponse(
                    status_code=200,
                    content={
                        "data": {
                            "filename": filename,
                            "extension": ext,
                            "chunks": result["chunks"],
                            "collection_count": result["collection_count"]
                        },
                        "message": "Document uploaded successfully",
                        "error": ""
                    }
                )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "data": [],
                "message": "",
                "error": str(e)
            }
        )

async def ask_question(request):

    try:
        query = request.get("query")
        feature = request.get("feature")
    
        retriever = get_answer_from_llm_vectorstore(query, feature)
        
        return JSONResponse(
                    status_code=200,
                    content={
                        "data": {
                            "content": retriever
                        },
                        "message": "Document uploaded successfully",
                        "error": ""
                    }
                )

    except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "data": [],
                    "message": "",
                    "error": str(e)
                }
            )

    

    
