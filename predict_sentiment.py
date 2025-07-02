from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

model_name = "Dakie/mongolian-bert-base-multilingual-cased"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

pipe = pipeline("text-classification", model=model, tokenizer=tokenizer)

result = pipe("үнэхээр гоё байна")
print(result)
