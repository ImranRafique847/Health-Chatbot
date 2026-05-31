"""
FastAPI Backend - Healthcare Chatbot
Connects to AWS Bedrock for medical Q&A (with streaming)
Also serves the frontend HTML
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import boto3
import json
import os
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

app = FastAPI(title="Healthcare Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = "amazon.nova-lite-v1:0"

from botocore.config import Config

boto_config = Config(
    read_timeout=120,
    connect_timeout=30,
    retries={"max_attempts": 3}
)

client = boto3.client(
    "bedrock-runtime",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
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


@app.post("/ask/stream")
async def ask_stream(q: Question):
    """Streaming endpoint - sends tokens as they are generated."""
    if not q.message.strip():
        raise HTTPException(status_code=400, detail="Empty question")

    def generate():
        try:
            response = client.converse_stream(
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

            stream = response.get("stream")
            if stream:
                for event in stream:
                    if "contentBlockDelta" in event:
                        delta = event["contentBlockDelta"]["delta"]
                        if "text" in delta:
                            yield f"data: {json.dumps({'text': delta['text']})}\n\n"

            yield "data: [DONE]\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


# Serve frontend
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")


@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
