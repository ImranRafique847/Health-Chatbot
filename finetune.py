"""
Fine-tune GPT-2 on Local Medical Data using LoRA
=================================================
Works on 4GB GPU (Quadro T1000).
After fine-tuning, the chatbot app uses AWS Bedrock for serving.
This script trains a local model for experimentation.

Dataset: ./data/medical_qa_dataset.json
Output:  ./medical-chatbot-finetuned/

Usage:   python finetune.py
"""

import os
import json
import torch
from torch.utils.data import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
)
from peft import LoraConfig, get_peft_model

# ======================================================
# Config
# ======================================================
MODEL_NAME = "gpt2"
DATASET_PATH = "./data/medical_qa_dataset.json"
OUTPUT_DIR = "./medical-chatbot-finetuned"

NUM_EPOCHS = 5
BATCH_SIZE = 2
GRADIENT_ACCUMULATION = 4
LEARNING_RATE = 3e-4
MAX_SEQ_LENGTH = 256


# ======================================================
# Dataset
# ======================================================
class MedicalQADataset(Dataset):
    def __init__(self, data, tokenizer, max_length):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.examples = []
        for item in data:
            text = (
                f"Question: {item['question']}\n"
                f"Answer: {item['answer']}\n<|endoftext|>"
            )
            self.examples.append(text)

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        enc = self.tokenizer(
            self.examples[idx],
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt",
        )
        input_ids = enc["input_ids"].squeeze()
        attention_mask = enc["attention_mask"].squeeze()
        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": input_ids.clone(),
        }


# ======================================================
# Main
# ======================================================
def main():
    print("=" * 50)
    print("  Fine-Tuning GPT-2 for Healthcare Chatbot")
    print("=" * 50)

    # Check GPU
    if torch.cuda.is_available():
        name = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"\n  GPU: {name} ({vram:.1f} GB)")
    else:
        print("\n  No GPU found, using CPU (will be slow)...")

    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Load data
    print(f"\n  Loading data from {DATASET_PATH}...")
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"  Loaded {len(data)} Q&A pairs")

    split = int(len(data) * 0.9)
    train_data = data[:split]
    val_data = data[split:]
    print(f"  Train: {len(train_data)} | Val: {len(val_data)}")

    # Load model
    print(f"\n  Loading {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    model.to(device)
    print("  Model loaded!")

    # Apply LoRA
    print("\n  Applying LoRA...")
    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["c_attn", "c_proj"],
    )
    model = get_peft_model(model, lora_config)

    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"  Trainable: {trainable:,} / {total:,} ({100*trainable/total:.2f}%)")

    # Datasets
    train_dataset = MedicalQADataset(train_data, tokenizer, MAX_SEQ_LENGTH)
    val_dataset = MedicalQADataset(val_data, tokenizer, MAX_SEQ_LENGTH)

    # Train
    print("\n  Starting training...\n")
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION,
        learning_rate=LEARNING_RATE,
        weight_decay=0.01,
        warmup_steps=10,
        logging_steps=5,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=1,
        fp16=torch.cuda.is_available(),
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
    )

    trainer.train()

    # Save
    print(f"\n  Saving to {OUTPUT_DIR}...")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    # Test
    print("\n  Testing...\n")
    model.eval()
    test_questions = [
        "What are the symptoms of diabetes?",
        "How is hypertension treated?",
    ]
    for q in test_questions:
        prompt = f"Question: {q}\nAnswer:"
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=100,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
            )
        answer = tokenizer.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        print(f"  Q: {q}")
        print(f"  A: {answer[:200]}\n")

    print("=" * 50)
    print("  DONE! Fine-tuning complete.")
    print("  Chatbot uses AWS Bedrock: streamlit run app.py")
    print("=" * 50)


if __name__ == "__main__":
    main()
