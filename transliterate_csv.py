import pandas as pd
import re
import os
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
from rules import latin_exclusions, normalization_dict, latin_to_cyrillic, digraphs

# Setup
output_folder = "D:/sentiment"
os.makedirs(output_folder, exist_ok=True)

# Rule tracking
rule_usage = defaultdict(int)
digraph_usage = defaultdict(int)

def is_cyrillic(text):
    return all('а' <= char <= 'я' or char == 'ё' for char in str(text).lower())

def normalize_text(text):
    if pd.isna(text):
        return ""
    text = str(text)
    words = text.split()
    normalized_words = []

    for word in words:
        lower = word.lower()
        if lower in latin_exclusions:
            normalized_words.append(word)
        elif lower.endswith("2"):
            base = lower[:-1]
            if base in normalization_dict:
                norm = normalization_dict[base]
                for w in norm.split():
                    rule_usage[f"{base} → {normalization_dict[base]}"] += 1
                    normalized_words.append(normalization_dict.get(w, w))
                for w in norm.split():
                    normalized_words.append(normalization_dict.get(w, w))
            else:
                normalized_words.append(word)
        else:
            norm = normalization_dict.get(lower, word)
            if norm != word:
                rule_usage[f"{lower} → {norm}"] += 1
            for w in norm.split():
                normalized_words.append(normalization_dict.get(w, w))
    return " ".join(normalized_words)

def fix_h_pronunciations(text):
    return re.sub(r'\bh([aeiouöü])', r'kh\1', str(text))

def transliterate_latin_to_cyrillic(text):
    result = []
    for word in str(text).split():
        lower = word.lower()
        if lower in latin_exclusions or is_cyrillic(lower):
            result.append(word)
            continue
        for digraph in digraphs:
            if digraph in latin_to_cyrillic:
                count = len(re.findall(digraph, word, flags=re.IGNORECASE))
                if count > 0:
                    digraph_usage[f"{digraph} → {latin_to_cyrillic[digraph]}"] += count
                    word = re.sub(digraph, latin_to_cyrillic[digraph], word, flags=re.IGNORECASE)
        if re.match(r'^(er|ev|ey)', word.lower()):
            word = re.sub(r'^[eE]', 'е', word)
        converted = ''
        for char in word:
            if char.lower() == 'e':
                converted += 'э'
            else:
                converted += latin_to_cyrillic.get(char.lower(), char)
        result.append(converted)
    return ' '.join(result)

def latin_to_cyrillic_pipeline(text):
    if pd.isna(text) or str(text).strip() == "":
        return ""
    text = fix_h_pronunciations(text)
    text = normalize_text(text)
    return transliterate_latin_to_cyrillic(text)

def plot_bar(data, title, output_path):
    top = [(k, v) for k, v in data.most_common(20) if isinstance(k, str)]
    if not top:
        print(f"No valid strings to plot for {title}")
        return
    labels, values = zip(*top)
    plt.figure(figsize=(10, 6))
    plt.barh(labels[::-1], values[::-1], color='skyblue')
    plt.xlabel("Count")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def process_and_analyze(input_excel, output_csv, latin_column):
    df = pd.read_excel(input_excel)
    if latin_column not in df.columns:
        raise ValueError(f"Column '{latin_column}' not found.")
    
    df['normalized'] = df[latin_column].apply(normalize_text)
    df['cyrillic'] = df['normalized'].apply(transliterate_latin_to_cyrillic)
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')

    # Sentence frequency
    sentence_counter = Counter(df[latin_column].dropna().str.strip().str.lower())
    pd.DataFrame(sentence_counter.items(), columns=['sentence', 'count']).sort_values(by="count", ascending=False)\
        .to_csv(f"{output_folder}/top_sentences.csv", index=False, encoding='utf-8-sig')
    plot_bar(sentence_counter, "Top Comments (Sentences)", f"{output_folder}/top_sentences_chart.png")

    # Word frequency
    word_counter = Counter()
    for row in df[latin_column].dropna():
    if isinstance(row, str):
        words = row.lower().split()
        word_counter.update(words)
    pd.DataFrame(word_counter.items(), columns=['word', 'count']).sort_values(by="count", ascending=False)\
        .to_csv(f"{output_folder}/top_words.csv", index=False, encoding='utf-8-sig')
    plot_bar(word_counter, "Top Words", f"{output_folder}/top_words_chart.png")

    # Rule usage
    rule_data = [{"rule_type": "normalization", "rule": k, "times_used": v} for k, v in rule_usage.items()]
    digraph_data = [{"rule_type": "digraph", "rule": k, "times_used": v} for k, v in digraph_usage.items()]
    rule_df = pd.DataFrame(rule_data + digraph_data).sort_values(by="times_used", ascending=False)
    rule_df.to_csv(f"{output_folder}/rule_usage_report.csv", index=False, encoding='utf-8-sig')

# Run
input_excel = "D:/sentiment/Facebook Comments 1.xlsx"
output_csv = "D:/sentiment/output_cyrillic.csv"
latin_column = "text"
process_and_analyze(input_excel, output_csv, latin_column)
