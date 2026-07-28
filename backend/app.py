from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from backend.router import api


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Start project")
    yield
    print("Shutting down")


app = FastAPI(
    title="Rag AI Resume Assistant",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"]
)

app.include_router(api.router)

@app.get("/")
async def health():
    return {"message": "hello"}