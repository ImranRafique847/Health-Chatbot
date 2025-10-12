import streamlit as st
import torch
import pickle
from transformers import AutoTokenizer, AutoModelForCausalLM

# ======================================================
# Load fine-tuned healthcare model (CPU-safe)
# ======================================================
@st.cache_resource
def load_model():
    MODEL_PATH = r"E:\PythonProject\Health Chatbot\phi2_healthcare_lora_cpu_clean.pkl"
    try:
        st.write("🔄 Loading healthcare model (CPU)...")

        # Safely load model dictionary
        with open(MODEL_PATH, "rb") as f:
            model_data = torch.load(f, map_location=torch.device("cpu"), weights_only=False)

        # The pickle file must contain a model and tokenizer
        model = model_data.get("model", None)
        tokenizer = model_data.get("tokenizer", None)

        if model is None or tokenizer is None:
            raise ValueError("Model or tokenizer missing in .pkl file")

        model.eval()
        return model, tokenizer

    except Exception as e:
        st.error(f"❌ Error loading model: {e}")
        return None, None


# ======================================================
# Initialize model + tokenizer
# ======================================================
model, tokenizer = load_model()

# ======================================================
# Streamlit App UI
# ======================================================
st.set_page_config(page_title="Healthcare Chatbot", page_icon="🩺", layout="wide")

st.sidebar.title("💬 Healthcare Chatbot")
st.sidebar.markdown("An AI-powered medical Q&A assistant using fine-tuned Phi-2 model.")

# --- Custom Styling ---
st.markdown("""
    <style>
        body {
            background-color: #0e1117;
            color: white;
        }
        .title {
            text-align: center;
            font-size: 48px;
            font-weight: bold;
            background: -webkit-linear-gradient(45deg, #00f5d4, #00bbf9);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 25px;
        }
        .response-box {
            background-color: #1e1e1e;
            padding: 18px;
            border-radius: 10px;
            color: white;
            font-size: 17px;
            line-height: 1.6;
        }
        .stTextInput > div > div > input {
            background-color: #222;
            color: white;
        }
        .stButton button {
            background-color: #00bbf9;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("<div class='title'>🩺 RAG Healthcare Chatbot</div>", unsafe_allow_html=True)

# ======================================================
# Chat Interface
# ======================================================
user_input = st.text_input("💭 Ask a medical question", placeholder="Type your question here...")

if st.button("Send"):
    if not user_input.strip():
        st.warning("⚠️ Please enter a question.")
    elif model is None or tokenizer is None:
        st.warning("⚠️ Model not loaded. Please check your .pkl file path.")
    else:
        with st.spinner("🤔 Thinking..."):
            try:
                inputs = tokenizer(user_input, return_tensors="pt")
                outputs = model.generate(**inputs, max_new_tokens=200)
                response = tokenizer.decode(outputs[0], skip_special_tokens=True)
                st.markdown("### 💬 Response:")
                st.markdown(f"<div class='response-box'>{response}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Error during generation: {e}")
