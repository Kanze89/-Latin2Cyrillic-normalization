from googletrans import Translator
from transformers import pipeline
import pandas as pd

translator = Translator()
sentiment = pipeline("sentiment-analysis")

def analyze(text):
    en = translator.translate(text, src='mn', dest='en').text
    res = sentiment(en)[0]
    return en, res["label"], round(res["score"], 4)

df = pd.read_csv("D:/sentiment/output_cyrillic.csv")
df["en"], df["sentiment"], df["score"] = zip(*df["cyrillic"].apply(analyze))
df.to_csv("D:/sentiment/output_with_sentiment.csv", index=False)
