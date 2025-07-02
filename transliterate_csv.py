from rules import latin_exclusions, normalization_dict, latin_to_cyrillic, digraphs
import pandas as pd
import re
import sys

# Fix Windows terminal encoding
sys.stdout.reconfigure(encoding='utf-8')

# ✅ Detect if word is already in Cyrillic
def is_cyrillic(text):
    return all('а' <= char <= 'я' or char == 'ё' for char in text.lower())

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
                        normalized_words.append(normalization_dict.get(w, w))
                    for w in norm.split():
                        normalized_words.append(normalization_dict.get(w, w))
                else:
                    normalized_words.append(word)
            else:
                norm = normalization_dict.get(lower, word)
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

# Step 4: Full pipeline
def latin_to_cyrillic_pipeline(text):
    if pd.isna(text) or str(text).strip() == "":
        return ""
    text = str(text)
    text = fix_h_pronunciations(text)
    text = normalize_text(text)
    return transliterate_latin_to_cyrillic(text)

# Step 5: Apply to Excel
def process_excel_to_csv(input_excel, output_csv, latin_column):
    df = pd.read_excel(input_excel)

    print("Column names in Excel:")
    for col in df.columns:
        print("-", col)

    if latin_column not in df.columns:
        raise ValueError(f"Column '{latin_column}' not found.")

    df['cyrillic'] = df[latin_column].apply(latin_to_cyrillic_pipeline)

    # ✅ Accuracy check if 'expected' column is present
    if 'expected' in df.columns:
        df['correct'] = df['cyrillic'] == df['expected']
        total = len(df)
        correct = df['correct'].sum()
        accuracy = round((correct / total) * 100, 2)
        print(f"\n✅ Accuracy: {correct}/{total} = {accuracy}%")

        # Export incorrect results for review
        errors = df[df['correct'] == False]
        if not errors.empty:
            error_path = "D:/sentiment/errors.csv"
            errors.to_csv(error_path, index=False, encoding='utf-8-sig')
            print(f"❌ Errors saved to: {error_path}")
    else:
        print("\n⚠️ No 'expected' column found. Skipping accuracy check.")

    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print("✅ Final output saved to:", output_csv)

# Step 6: Run
if __name__ == "__main__":
    input_excel = "D:/sentiment/Facebook Comments 1.xlsx"
    output_csv = "D:/sentiment/output_cyrillic.csv"
    latin_column = "text"  # Your actual column name

    process_excel_to_csv(input_excel, output_csv, latin_column)
