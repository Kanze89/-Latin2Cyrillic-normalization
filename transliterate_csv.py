from rules import latin_exclusions, normalization_dict, latin_to_cyrillic, digraphs
import pandas as pd
import re
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

# ✅ Detect if word is already in Cyrillic
def is_cyrillic(text):
    return all('а' <= char <= 'я' or char == 'ё' for char in text.lower())

# 🔁 Track rule usage
rule_usage = defaultdict(int)
digraph_usage = defaultdict(int)

# Step 1: Normalize informal patterns
def normalize_text(text):
    words = text.split()
    normalized_words = []

    for word in words:
        lower = word.lower()

        if lower in latin_exclusions:
            normalized_words.append(word)
        else:
            if lower.endswith("2"):
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

# Step 2: Fix "h" used instead of "kh"
def fix_h_pronunciations(text):
    return re.sub(r'\bh([aeiouöü])', r'kh\1', text)

# Step 3: Transliterate Latin to Cyrillic
def transliterate_latin_to_cyrillic(text):
    result = []

    for word in text.split():
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

# Full pipeline
def latin_to_cyrillic_pipeline(text):
    if pd.isna(text) or str(text).strip() == "":
        return ""
    text = str(text)
    text = fix_h_pronunciations(text)
    text = normalize_text(text)
    return transliterate_latin_to_cyrillic(text)

# Main processor
def process_and_analyze(input_excel, output_folder, latin_column):
    df = pd.read_excel(input_excel)

    if latin_column not in df.columns:
        raise ValueError(f"Column '{latin_column}' not found.")

    # Count top comments
    comment_counts = Counter(df[latin_column].dropna().str.strip().str.lower())

    df['normalized'] = df[latin_column].apply(normalize_text)
    df['cyrillic'] = df['normalized'].apply(transliterate_latin_to_cyrillic)

    # Save main output
    df.to_csv(f"{output_folder}/output_cyrillic.csv", index=False, encoding='utf-8-sig')

    # Save top comment frequency
    top_comments_df = pd.DataFrame(comment_counts.items(), columns=['comment', 'count']).sort_values(by='count', ascending=False)
    top_comments_df.to_csv(f"{output_folder}/top_comments.csv", index=False, encoding='utf-8-sig')

    # Save rule usage
    rule_data = [{"rule_type": "normalization", "rule": k, "times_used": v} for k, v in rule_usage.items()]
    digraph_data = [{"rule_type": "digraph", "rule": k, "times_used": v} for k, v in digraph_usage.items()]
    rule_report_df = pd.DataFrame(rule_data + digraph_data)
    rule_report_df.to_csv(f"{output_folder}/rule_usage_report.csv", index=False, encoding='utf-8-sig')

    print("✅ Saved:")
    print("- output_cyrillic.csv")
    print("- top_comments.csv")
    print("- rule_usage_report.csv")

# === RUN ===
if __name__ == "__main__":
    input_excel = "D:/sentiment/Facebook Comments 1.xlsx"
    output_folder = "D:/sentiment"
    latin_column = "text"

    process_and_analyze(input_excel, output_folder, latin_column)
