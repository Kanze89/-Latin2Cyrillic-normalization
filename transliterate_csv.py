import pandas as pd
import re
import sys

# Fix terminal encoding to avoid UnicodeEncodeError
sys.stdout.reconfigure(encoding='utf-8')

# Step 1: Normalization dictionary (you can expand this list)
normalization_dict = {
    "bn": "baina",
    "bnu": "baina uu",
    "zugeer": "zugeer",
    "zgr": "zugeer",
    "mngl": "mongol",
    "ymr": "yamar",
    "ymar": "yamar",
    "yu": "yuu",
    "xar": "khar",
    "xap": "khar",
    "har": "khar",
    "hun": "xun",
    "huts": "xuts",
    "hotiin": "xotiin",
    "hureerei": "xureerei",
    "hicheel": "xicheel",
    "xun": "xun",
}

# Step 2: Latin to Cyrillic mapping
latin_to_cyrillic = {
    "ch": "ч", "sh": "ш", "ts": "ц", "ya": "я", "yo": "ё", "yu": "ю", "ee": "э",
    "a": "а", "b": "б", "c": "ц", "d": "д", "e": "е", "f": "ф", "g": "г",
    "h": "х", "i": "и", "j": "ж", "k": "к", "l": "л", "m": "м", "n": "н",
    "o": "о", "p": "п", "q": "к", "r": "р", "s": "с", "t": "т", "u": "у",
    "v": "в", "w": "в", "x": "х", "y": "й", "z": "з"
}

# Step 3: Normalize informal words
def normalize_text(text):
    words = text.split()
    normalized_words = [normalization_dict.get(word.lower(), word) for word in words]
    return " ".join(normalized_words)

# Step 4: Fix h used as x
def fix_h_pronunciations(text):
    return re.sub(r'\bh([aeiou])', r'kh\1', text)

# Step 5: Transliterate to Cyrillic
def transliterate_latin_to_cyrillic(text):
    digraphs = ["ch", "sh", "ts", "ya", "yo", "yu", "ee"]
    for digraph in digraphs:
        if digraph in latin_to_cyrillic:
            text = re.sub(digraph, latin_to_cyrillic[digraph], text, flags=re.IGNORECASE)

    result = ''
    for char in text:
        lower_char = char.lower()
        result += latin_to_cyrillic.get(lower_char, char)
    return result

# Step 6: Full pipeline
def latin_to_cyrillic_pipeline(text):
    if pd.isna(text):
        return ""
    text = str(text)
    text = fix_h_pronunciations(text)
    text = normalize_text(text)
    return transliterate_latin_to_cyrillic(text)

# Step 7: Process Excel and output CSV
def process_excel_to_csv(input_excel, output_csv, latin_column):
    df = pd.read_excel(input_excel)

    print("Column names in Excel:")
    for col in df.columns:
        print("-", col)

    # Apply transliteration
    df['cyrillic'] = df[latin_column].apply(latin_to_cyrillic_pipeline)

    # Save to CSV
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print("Saved CSV to:", output_csv)

# Step 8: Main run block
if __name__ == "__main__":
    input_excel = "D:/sentiment/Facebook Comments 1.xlsx"   # your input file
    output_csv = "D:/sentiment/output_cyrillic.csv"         # your output file
    latin_column = "Comment"                                # replace with exact column name

    process_excel_to_csv(input_excel, output_csv, latin_column)
