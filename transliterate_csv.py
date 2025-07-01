import pandas as pd
import re
import sys

# Fix Windows terminal encoding
sys.stdout.reconfigure(encoding='utf-8')

# Words to skip transliteration (e.g. brands, apps, platforms)
latin_exclusions = {
    "univision", "unuvision", "univishion", "voo", "skymedia", "mobinet", "unitel", "computer", "windows xp", "uni"
}

# Normalization dictionary: informal or fixed forms
normalization_dict = {
    "bn": "baina", "bna": "baina",
    "bga": "baigaa",
    "bdin": "baidag yum",
    "bdg": "baidag", "bdag": "baidag",
    "bnu": "baina uu",
    "zugeer": "zugeer",
    "zgr": "zugeer",
    "mngl": "mongol",
    "ymr": "yamar",
    "ymar": "yamar",
    "yu": "yuu", "yuu": "yuu",
    "xar": "khar", "xap": "khar", "har": "khar",
    "hun": "xun",
    "huts": "xuts",
    "hotiin": "xotiin",
    "hureerei": "hureerei",
    "hicheel": "hicheel",
    "xun": "xun",
    "tuhuurumj": "töhöörömj",
    "buren": "büren",
    "zuv": "zöv",
    "hereg": "khereg",
    "deer": "deer",
    "mungu": "möngö", "mongo": "möngö",
    "shuu": "shüü", "shvv": "shüü",
    "hymd": "hyamd",
    "hynalt": "hyanalt",
    "ym": "yum", "yum": "юм",  # ✅ final Cyrillic form
    "tuv": "töv", "tuw": "töv"
}

# Latin to Cyrillic mapping
latin_to_cyrillic = {
    "ui": "уй", "vi": "үй", "üi": "үй", "ai": "ай", "ii": "ий", "kh": "х",
    "ch": "ч", "sh": "ш", "ts": "ц", "ya": "я", "yo": "ё", "yu": "ю", "ee": "э",
    "ö": "ө", "ü": "ү",
    "a": "а", "b": "б", "c": "ц", "d": "д", "e": "е", "f": "ф", "g": "г",
    "h": "х", "i": "и", "j": "ж", "k": "к", "l": "л", "m": "м", "n": "н",
    "o": "о", "p": "п", "q": "к", "r": "р", "s": "с", "t": "т", "u": "у",
    "v": "в", "w": "в", "x": "х", "y": "й", "z": "з"
}

# Digraphs ordered by priority (longest first)
digraphs = ["kh", "üi", "vi", "ui", "ai", "ii", "ch", "sh", "ts", "ya", "yo", "yu", "ee"]

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

        if re.match(r'^(er|ev|ey), word.lower'()):
            word = re.sub(r'^[eE]', 'e', word)

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
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print("Saved to:", output_csv)

# Step 6: Run
if __name__ == "__main__":
    input_excel = "D:/sentiment/Facebook Comments 1.xlsx"
    output_csv = "D:/sentiment/output_cyrillic.csv"
    latin_column = "text"  # Your actual column name

    process_excel_to_csv(input_excel, output_csv, latin_column)
