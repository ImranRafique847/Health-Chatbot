# 🩺 Healthcare Chatbot

AI-powered healthcare assistant that answers medical questions using AWS Bedrock.

## 🔴 Live Demo

**[👉 Try it live here](https://6c9gnud1jh.execute-api.us-east-1.amazonaws.com/)**

---

## Features

- Medical Q&A powered by AWS Bedrock (Amazon Nova Lite)
- Modern, clean UI (doesn't look like a typical AI chatbot)
- Quick topic suggestions (Heart, Respiratory, Mental Health, etc.)
- Real-time streaming responses
- Deployed on AWS Lambda with Docker

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, FastAPI, Mangum
- **AI Model:** Amazon Nova Lite (via AWS Bedrock)
- **Deployment:** AWS Lambda, ECR, API Gateway, Docker

## Project Structure

```
Health-Chatbot/
├── backend/          # FastAPI server (local development)
├── frontend/         # HTML/CSS/JS UI
├── deploy/           # Docker + Lambda deployment files
├── data/             # Medical Q&A training dataset
├── finetune.py       # Fine-tuning script (GPT-2 + LoRA)
├── .env              # AWS credentials (not in repo)
└── README.md
```

## Run Locally

```bash
cd backend
pip install fastapi uvicorn boto3 python-dotenv
uvicorn main:app --reload --port 8000
```

Then open http://localhost:8000

## Disclaimer

⚠️ This chatbot provides general health information only. It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider.
