import pandas as pd
from datasets import Dataset
from transformers import (
    BertTokenizer, BertForSequenceClassification,
    Trainer, TrainingArguments, DataCollatorWithPadding
)
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import numpy as np

# === CONFIG ===
model_name = "bert-base-mongolian-cased"
csv_path = "D:/sentiment/output_cyrillic.csv"  # CSV with 'cyrillic' and 'sentiment' columns
output_dir = "./mnbert-sentiment"

# === 1. Load and Encode Dataset ===
df = pd.read_csv(csv_path)

# Map sentiment labels to integers
label_map = {"positive": 0, "negative": 1, "neutral": 2}
df["label"] = df["sentiment"].map(label_map)

# Use 'cyrillic' column as input text
df = df[["cyrillic", "label"]].dropna()
df = df.rename(columns={"cyrillic": "text"})

# Convert to HuggingFace dataset
dataset = Dataset.from_pandas(df)

# Split train/test
dataset = dataset.train_test_split(test_size=0.2, seed=42)
train_data = dataset["train"]
eval_data = dataset["test"]

# === 2. Load Tokenizer and Model ===
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name, num_labels=3)

# Tokenization function
def tokenize(batch):
    return tokenizer(batch["text"], truncation=True, padding=True)

# Apply tokenization
train_data = train_data.map(tokenize, batched=True)
eval_data = eval_data.map(tokenize, batched=True)

# === 3. Define Evaluation Metrics ===
def compute_metrics(pred):
    labels = pred.label_ids
    preds = np.argmax(pred.predictions, axis=1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average="weighted")
    acc = accuracy_score(labels, preds)
    return {
        "accuracy": acc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }

# === 4. Training Configuration ===
training_args = TrainingArguments(
    output_dir=output_dir,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    logging_strategy="steps",
    logging_steps=50,
    num_train_epochs=4,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    learning_rate=2e-5,
    weight_decay=0.01,
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    save_total_limit=2
)

# === 5. Trainer Setup ===
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_data,
    eval_dataset=eval_data,
    tokenizer=tokenizer,
    data_collator=DataCollatorWithPadding(tokenizer),
    compute_metrics=compute_metrics,
)

# === 6. Train the Model ===
trainer.train()

# === 7. Save the Final Model ===
trainer.save_model(f"{output_dir}/final")
