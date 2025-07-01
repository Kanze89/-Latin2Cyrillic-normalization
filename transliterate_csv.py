import pandas as pd
import re
import sys

# Fix Windows terminal encoding
sys.stdout.reconfigure(encoding='utf-8')

# Words to skip transliteration (e.g. brands)
latin_exclusions = {"univision"}

# Normalization dictionary: informal or fixed forms
normalization_dict = {
    "bn": "baina",
    "bnu": "baina uu",
    "zugeer": "zugeer",
    "zgr": "zugeer",
    "mngl": "mongol",
    "ymr": "yamar",
    "ymar": "yamar",
    "yu": "yuu",
    "xar": "khar", "xap": "khar", "har": "khar",
    "hun": "xun",
    "huts": "xuts",
    "hotiin": "xotiin",
    "hureerei": "xureerei",
    "hicheel": "xicheel",
    "xun": "xun",
    "tuhuurumj": "tökhöörömj",   # төхөөрөмж
    "buren": "büren",           # бүрэн
    "zuv": "zöv",               # зөв
    "hereg": "khereg",          # хэрэг
    "deer": "deer",             # дээр
    "mungu": "möngö"
}

# Latin to Cyrillic mapping (includes ö, ü, ui/vi/üi)
latin_to_cyrillic = {
    "ui": "уй", "vi": "үй", "üi": "үй",
    "ch": "ч", "sh": "ш", "ts": "ц", "ya": "я", "yo": "ё", "yu": "ю", "ee": "э",
    "ö": "ө", "ü": "ү",
    "a": "а", "b": "б", "c": "ц", "d": "д", "e": "е", "f": "ф", "g": "г",
    "h": "х", "i": "и", "j": "ж", "k": "к", "l": "л", "m": "м", "n": "н",
    "o": "о", "p": "п", "q": "к", "r": "р", "s": "с", "t": "т", "u": "у",
    "v": "в", "w": "в", "x": "х", "y": "й", "z": "з"
}

# Digraphs ordered by priority (longest first)
digraphs = ["üi", "vi", "ui", "ch", "sh", "ts", "ya", "yo", "yu", "ee"]

# Normalize slang and fixed words
def normalize_text(text):
    words = text.split()
    normalized_words = []
    for word in words:
        lower = word.lower()
        if lower in latin_exclusions:
            normalized_words.append(word)
        else:
            normalized_words.append(normalization_dict.get(lower, word))
    return " ".join(normalized_words)

# Fix h used instead of kh
def fix_h_pronunciations(text):
    return re.sub(r'\bh([aeiouöü])', r'kh\1', text)

# Transliterate Latin to Cyrillic
def transliterate_latin_to_cyrillic(text):
    # Step 1: Replace digraphs (longest first)
    for digraph in digraphs:
        if digraph in latin_to_cyrillic:
            text = re.sub(digraph, latin_to_cyrillic[digraph], text, flags=re.IGNORECASE)

    # Step 2: Replace word-initial "e" with "е"
    text = re.sub(r'\b[eE]', 'е', text)

    # Step 3: Transliterate word-by-word, skipping exclusions
    result = []
    for word in text.split():
        if word.lower() in latin_exclusions:
            result.append(word)  # Leave brand name untouched
        else:
            converted = ''
            for char in word:
                if char.lower() == 'e':
                    converted += 'э'
                else:
                    converted += latin_to_cyrillic.get(char.lower(), char)
            result.append(converted)

    return ' '.join(result)

# Full pipeline: normalize → fix h → transliterate
def latin_to_cyrillic_pipeline(text):
    if pd.isna(text):
        return ""
    text = str(text)
    text = fix_h_pronunciations(text)
    text = normalize_text(text)
    return transliterate_latin_to_cyrillic(text)

# Main processing function
def process_excel_to_csv(input_excel, output_csv, latin_column):
    df = pd.read_excel(input_excel)

    print("Column names in Excel:")
    for col in df.columns:
        print("-", col)

    if latin_column not in df.columns:
        raise ValueError(f"Column '{latin_column}' not found.")

    df['cyrillic'] = df[latin_column].apply(latin_to_cyrillic_pipeline)
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print("Saved to:", output_csv)

# Run script
if __name__ == "__main__":
    input_excel = "D:/sentiment/Facebook Comments 1.xlsx"
    output_csv = "D:/sentiment/output_cyrillic.csv"
    latin_column = "text"  # your column name

    process_excel_to_csv(input_excel, output_csv, latin_column)
