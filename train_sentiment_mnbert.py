import pandas as pd
import sys
from datasets import Dataset
from transformers import (
    BertTokenizer, BertForSequenceClassification,
    Trainer, TrainingArguments, DataCollatorWithPadding
)
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import numpy as np

# Fix terminal encoding (for printing Cyrillic column names)
sys.stdout.reconfigure(encoding='utf-8')

# === CONFIG ===
model_name = "bert-base-mongolian-cased"
csv_path = "D:/sentiment/labeled_data.csv"  # Make sure it contains 'text' and 'sentiment' columns
output_dir = "./mnbert-sentiment"

# === 1. Load CSV and Inspect Columns ===
df = pd.read_csv(csv_path)
print("Column names:", df.columns.tolist())

# === 2. Label Encoding ===
label_map = {"positive": 0, "negative": 1, "neutral": 2}
df["label"] = df["sentiment"].map(label_map)

# Use the 'text' column (already in Cyrillic if prepared)
df = df[["text", "label"]].dropna()

# Convert to HuggingFace Dataset
dataset = Dataset.from_pandas(df)
dataset = dataset.train_test_split(test_size=0.2, seed=42)
train_data = dataset["train"]
eval_data = dataset["test"]

# === 3. Load Tokenizer and Model ===
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name, num_labels=3)

def tokenize(batch):
    return tokenizer(batch["text"], truncation=True, padding=True)

train_data = train_data.map(tokenize, batched=True)
eval_data = eval_data.map(tokenize, batched=True)

# === 4. Metrics Function ===
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

# === 5. Training Configuration ===
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

# === 6. Trainer Setup ===
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_data,
    eval_dataset=eval_data,
    tokenizer=tokenizer,
    data_collator=DataCollatorWithPadding(tokenizer),
    compute_metrics=compute_metrics,
)

# === 7. Train ===
trainer.train()

# === 8. Save Final Model ===
trainer.save_model(f"{output_dir}/final")
