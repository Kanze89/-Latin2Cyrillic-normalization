import pandas as pd
from transformers import pipeline

# === Load input CSV ===
input_path = "D:/sentiment/output_cyrillic.csv"
df = pd.read_csv(input_path)
assert "cyrillic" in df.columns, "❌ Missing 'cyrillic' column in your CSV"

# === Load transformers pipelines ===
translate_mn2en = pipeline("translation", model="Helsinki-NLP/opus-mt-mn-en")
sentiment_en = pipeline("sentiment-analysis")  # uses default English BERT

# === Processing function ===
def analyze_sentiment(text):
    if pd.isna(text) or str(text).strip() == "":
        return {"en": "", "sentiment": "", "score": 0.0}

    # Translate to English
    try:
        en = translate_mn2en(text)[0]["translation_text"]
    except:
        en = ""

    # Sentiment analysis
    try:
        result = sentiment_en(en)[0]
        label = result["label"]     # e.g. POSITIVE / NEGATIVE
        score = round(result["score"], 4)
    except:
        label, score = "", 0.0

    return {"en": en, "sentiment": label, "score": score}

# === Apply to all rows ===
results = df["cyrillic"].apply(analyze_sentiment)
df["translated_en"] = results.apply(lambda x: x["en"])
df["sentiment_label"] = results.apply(lambda x: x["sentiment"])
df["sentiment_score"] = results.apply(lambda x: x["score"])

# === Save to new CSV ===
output_path = "D:/sentiment/output_translated_sentiment.csv"
df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"✅ Done. Saved to: {output_path}")
