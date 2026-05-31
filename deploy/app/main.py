"""
Healthcare Chatbot - Lambda Deployment
FastAPI app served via Mangum (Lambda adapter)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from mangum import Mangum
import boto3
import json
import os
from botocore.config import Config

app = FastAPI(title="Healthcare Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In Lambda, credentials come from IAM role (no .env needed)
AWS_REGION = os.getenv("BEDROCK_REGION", os.getenv("AWS_REGION", "us-east-1"))
MODEL_ID = os.getenv("MODEL_ID", "amazon.nova-lite-v1:0")

boto_config = Config(
    read_timeout=120,
    connect_timeout=30,
    retries={"max_attempts": 3}
)

client = boto3.client(
    "bedrock-runtime",
    region_name=AWS_REGION,
    config=boto_config,
)

SYSTEM_PROMPT = (
    "You are a knowledgeable healthcare assistant. "
    "Answer the following medical question accurately and helpfully. "
    "Always provide a COMPLETE answer - do not leave responses unfinished. "
    "Keep your answer concise but thorough. Use bullet points for clarity. "
    "Always end with a reminder to consult a doctor for serious concerns."
)


class Question(BaseModel):
    message: str


@app.post("/ask")
async def ask_question(q: Question):
    """Non-streaming endpoint (Lambda doesn't support true streaming via API Gateway)."""
    if not q.message.strip():
        raise HTTPException(status_code=400, detail="Empty question")

    try:
        response = client.converse(
            modelId=MODEL_ID,
            system=[{"text": SYSTEM_PROMPT}],
            messages=[
                {"role": "user", "content": [{"text": q.message}]}
            ],
            inferenceConfig={
                "maxTokens": 1024,
                "temperature": 0.5,
                "topP": 0.9,
            }
        )
        reply = response["output"]["message"]["content"][0]["text"].strip()
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "ok"}


# Serve frontend
FRONTEND_DIR = "/app/frontend"


@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# Lambda handler
handler = Mangum(app)
