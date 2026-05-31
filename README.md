# 🩺 Healthcare Chatbot — AI-Powered Medical Assistant

An intelligent healthcare chatbot that provides accurate medical information using AWS Bedrock's foundation models. Built with a modern web interface and deployed as a serverless application on AWS Lambda.

## 🔴 Live Demo

**[👉 Try the Live Application Here](https://6c9gnud1jh.execute-api.us-east-1.amazonaws.com/)**

---

## 📋 Problem Statement

Access to reliable healthcare information is a challenge for many people, especially in areas with limited medical resources. Patients often search the internet for health-related queries and receive unreliable or incomplete information. There is a need for an intelligent, accessible, and always-available healthcare assistant that can:

- Answer common medical questions accurately
- Provide dietary and lifestyle recommendations for various conditions
- Offer first-aid guidance and symptom information
- Remind users to consult qualified healthcare professionals for serious concerns

This project addresses this gap by building an AI-powered healthcare chatbot that leverages large language models to provide helpful, accurate, and responsible medical information.

---

## 🎯 Objectives

1. Build a conversational healthcare assistant using state-of-the-art AI models
2. Create a modern, user-friendly interface that feels like a medical app (not a generic AI chatbot)
3. Deploy the application as a scalable, serverless solution on AWS
4. Implement fine-tuning capabilities on medical datasets for improved domain accuracy
5. Ensure responsible AI usage with appropriate disclaimers and safety measures

---

## 🛠️ Tech Stack & Tools

| Category | Technology |
|----------|-----------|
| **AI/ML Model** | Amazon Nova Lite (via AWS Bedrock) |
| **Backend** | Python 3.11, FastAPI, Mangum |
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla) |
| **Cloud Provider** | Amazon Web Services (AWS) |
| **Deployment** | AWS Lambda, Amazon ECR, API Gateway |
| **Containerization** | Docker |
| **Fine-Tuning** | PyTorch, Hugging Face Transformers, PEFT (LoRA) |
| **Dataset** | MedQuAD (Medical Question Answering Dataset) |
| **Version Control** | Git, GitHub |
| **API Communication** | REST API, Server-Sent Events (SSE) |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      USER (Browser)                       │
│                                                          │
│   ┌─────────────────────────────────────────────────┐   │
│   │          Frontend (HTML/CSS/JS)                  │   │
│   │   - Chat Interface                              │   │
│   │   - Quick Topic Suggestions                     │   │
│   │   - Streaming Response Display                  │   │
│   └──────────────────────┬──────────────────────────┘   │
└──────────────────────────┼──────────────────────────────┘
                           │ HTTP POST /ask
                           ▼
┌──────────────────────────────────────────────────────────┐
│                   AWS API Gateway                         │
│              (HTTP API - Public Endpoint)                 │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                    AWS Lambda                             │
│         (Docker Container - Python 3.11)                 │
│                                                          │
│   ┌─────────────────────────────────────────────────┐   │
│   │           FastAPI + Mangum                       │   │
│   │   - Receives user question                      │   │
│   │   - Formats prompt with system instructions     │   │
│   │   - Calls Bedrock API                           │   │
│   │   - Returns AI-generated response               │   │
│   └──────────────────────┬──────────────────────────┘   │
└──────────────────────────┼───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                   AWS Bedrock                             │
│            (Amazon Nova Lite v1 Model)                    │
│                                                          │
│   - Processes medical queries                            │
│   - Generates accurate health information                │
│   - Provides complete, structured answers                │
└──────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Health-Chatbot/
│
├── backend/                    # Local development server
│   ├── main.py                 # FastAPI app with streaming support
│   └── requirements.txt        # Python dependencies
│
├── frontend/                   # User interface
│   ├── index.html              # Main HTML page
│   ├── style.css               # Styling (modern healthcare theme)
│   └── script.js               # Chat logic, API calls, streaming
│
├── deploy/                     # AWS Lambda deployment
│   ├── app/
│   │   ├── main.py             # Lambda-optimized FastAPI app
│   │   └── requirements.txt    # Production dependencies
│   ├── frontend/               # Frontend files for Lambda
│   │   ├── index.html
│   │   ├── style.css
│   │   └── script.js
│   ├── Dockerfile              # Container definition
│   ├── deploy.ps1              # Automated deployment script
│   └── trust-policy.json       # IAM trust policy
│
├── data/                       # Training data
│   └── medical_qa_dataset.json # 40 medical Q&A pairs
│
├── finetune.py                 # Fine-tuning script (GPT-2 + LoRA)
├── .env                        # AWS credentials (not in repo)
├── .gitignore                  # Ignored files
├── requirements.txt            # Project dependencies
└── README.md                   # This file
```

---

## 🔧 How It Works

### 1. User Interaction
- User opens the web application in a browser
- Types a health-related question or clicks a quick topic suggestion
- The frontend sends the question to the backend API

### 2. Backend Processing
- FastAPI receives the HTTP POST request
- Constructs a prompt with a medical system instruction
- Sends the prompt to AWS Bedrock's Nova Lite model
- Receives the AI-generated response

### 3. AI Response Generation
- AWS Bedrock processes the query using Amazon Nova Lite
- The model generates a medically-informed response
- Response includes structured information with bullet points
- Always includes a reminder to consult a healthcare professional

### 4. Response Delivery
- **Local mode:** Streaming (word-by-word) via Server-Sent Events
- **Lambda mode:** Complete response returned at once
- Frontend displays the response with proper formatting

---

## 🧠 Fine-Tuning Approach

This project includes a fine-tuning pipeline for training a local model on medical data:

### Dataset
- **Source:** MedQuAD (Medical Question Answering Dataset) + custom Q&A pairs
- **Size:** 40 curated medical Q&A pairs (expandable)
- **Format:** JSON with question-answer pairs
- **Topics:** Diabetes, hypertension, cancer, mental health, respiratory diseases, etc.

### Method
- **Base Model:** GPT-2 (124M parameters)
- **Technique:** LoRA (Low-Rank Adaptation) — trains only 1-2% of parameters
- **Hardware:** Optimized for 4GB VRAM GPU (Quadro T1000)
- **Training:** 5 epochs, batch size 2, learning rate 3e-4

### Why LoRA?
- Full fine-tuning of large models requires expensive hardware
- LoRA adds small trainable adapters to the model
- Reduces memory usage by 90%+ while maintaining quality
- Allows fine-tuning on consumer GPUs

---

## 🚀 Deployment Process

### Step 1: Containerization (Docker)
```dockerfile
FROM public.ecr.aws/lambda/python:3.11
COPY app/requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt
COPY app/main.py ${LAMBDA_TASK_ROOT}/
COPY frontend/ /app/frontend/
CMD ["main.handler"]
```

### Step 2: Push to Amazon ECR
```bash
docker build --platform linux/amd64 --provenance=false -t healthcare-chatbot:latest .
docker tag healthcare-chatbot:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/healthcare-chatbot:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/healthcare-chatbot:latest
```

### Step 3: Create AWS Lambda Function
- Package type: Docker Image
- Memory: 512 MB
- Timeout: 120 seconds
- IAM Role: Lambda execution + Bedrock full access

### Step 4: Expose via API Gateway
- HTTP API created with API Gateway v2
- Public endpoint with no authentication
- Routes all traffic to Lambda function

---

## 💻 Run Locally

### Prerequisites
- Python 3.11+
- AWS account with Bedrock access enabled
- AWS credentials configured

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/ImranRafique847/Health-Chatbot.git
cd Health-Chatbot
```

2. **Create .env file**
```
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_REGION=us-east-1
```

3. **Install dependencies**
```bash
pip install fastapi uvicorn boto3 python-dotenv
```

4. **Run the server**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

5. **Open in browser**
```
http://localhost:8000
```

---

## 🧪 Fine-Tune Locally

To fine-tune GPT-2 on the medical dataset:

```bash
pip install torch transformers peft
python finetune.py
```

This trains on your GPU (4GB+ VRAM required) using the data in `data/medical_qa_dataset.json`.

---

## 🌟 Key Features

| Feature | Description |
|---------|-------------|
| **Medical Q&A** | Answers health questions about symptoms, treatments, diet, medications |
| **Quick Topics** | One-click access to common health categories |
| **Modern UI** | Clean, professional healthcare-themed interface |
| **Streaming** | Real-time word-by-word response generation (local mode) |
| **Serverless** | Deployed on AWS Lambda — scales automatically, pay per use |
| **Containerized** | Docker-based deployment for consistency |
| **Fine-Tuning** | Includes LoRA-based fine-tuning pipeline for custom training |
| **Responsible AI** | Includes disclaimers and reminders to consult doctors |

---

## 📊 AWS Services Used

| Service | Purpose |
|---------|---------|
| **AWS Bedrock** | AI model inference (Amazon Nova Lite) |
| **AWS Lambda** | Serverless compute for the backend |
| **Amazon ECR** | Docker container registry |
| **API Gateway** | Public HTTP endpoint |
| **IAM** | Role-based access control |

---

## 🔒 Security Considerations

- AWS credentials stored in `.env` file (excluded from git via `.gitignore`)
- Lambda uses IAM role for Bedrock access (no hardcoded credentials in production)
- API Gateway provides a managed, secure endpoint
- No patient data is stored — all conversations are stateless

---

## 📈 Future Improvements

- [ ] Add RAG (Retrieval-Augmented Generation) with medical knowledge base
- [ ] Implement conversation memory for follow-up questions
- [ ] Add multi-language support (Urdu, Hindi, Arabic)
- [ ] Integrate with medical databases (PubMed, WHO)
- [ ] Add voice input/output capability
- [ ] Implement user authentication for personalized health tracking
- [ ] Fine-tune on larger medical datasets (MedQuAD 16k+, PubMedQA)
- [ ] Add symptom checker with structured questionnaire

---

## 👨‍💻 Author

**Imran Rafique**
- GitHub: [@ImranRafique847](https://github.com/ImranRafique847)

---

## ⚠️ Disclaimer

This chatbot is designed for **informational purposes only**. It does NOT provide medical diagnoses, prescriptions, or treatment plans. The information provided should not be used as a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of a qualified healthcare provider with any questions regarding a medical condition.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
