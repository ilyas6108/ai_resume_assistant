from pydantic import BaseModel

class UploadDocument(BaseModel):
    filename: str
    extension: str
    message: str

class AskQuery(BaseModel):
    query: str
    feature: str