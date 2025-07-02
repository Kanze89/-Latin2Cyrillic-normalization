import pandas as pd
from transformers import pipeline

# === Load your Cyrillic dataset ===
df = pd.read_csv("D:/sentiment/output_cyrillic.csv")
assert "cyrillic" in df.columns, "Make sure your file has a 'cyrillic' column"

# === Load pipelines ===
mn2en = pipeline("translation", model="Helsinki-NLP/opus-mt-mn-en")
en2mn = pipeline("translation", model="Helsinki-NLP/opus-mt-en-mn")
sentiment = pipeline("sentiment-analysis")  # default English BERT model

# === Define processing function ===
def analyze_sentiment_mn(text):
    if pd.isna(text) or str(text).strip() == "":
        return {"en": "", "sentiment": "", "mn_label": ""}
    
    # Translate to English
    translated = mn2en(text)[0]['translation_text']

    # Sentiment in English
    result = sentiment(translated)[0]
    label = result['label']  # e.g., POSITIVE or NEGATIVE

    # Translate label back to Mongolian
    mn_label = en2mn(label)[0]['translation_text']

    return {
        "en": translated,
        "sentiment": label,
        "mn_label": mn_label
    }

# === Apply to all rows ===
results = df["cyrillic"].apply(analyze_sentiment_mn)
df["translated_en"] = results.apply(lambda x: x["en"])
df["sentiment_en"] = results.apply(lambda x: x["sentiment"])
df["sentiment_mn"] = results.apply(lambda x: x["mn_label"])

# === Save output ===
df.to_csv("D:/sentiment/output_translated_sentiment.csv", index=False, encoding="utf-8-sig")
print("✅ Sentiment analysis complete. File saved.")
