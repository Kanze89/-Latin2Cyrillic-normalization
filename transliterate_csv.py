import pandas as pd
import re

# Step 1: Normalization dictionary for informal/abbreviated Latin Mongolian
normalization_dict = {
    "bn": "baina",
    "bnu": "baina uu",
    "zgr": "zugaar",
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

# Step 2: Latin → Cyrillic mapping
latin_to_cyrillic = {
    "ch": "ч", "sh": "ш", "ts": "ц", "ya": "я", "yo": "ё", "yu": "ю", "ee": "э",
    "a": "а", "b": "б", "c": "ц", "d": "д", "e": "е", "f": "ф", "g": "г",
    "h": "х", "i": "и", "j": "ж", "k": "к", "l": "л", "m": "м", "n": "н",
    "o": "о", "p": "п", "q": "к", "r": "р", "s": "с", "t": "т", "u": "у",
    "v": "в", "w": "в", "x": "х", "y": "й", "z": "з"
}

# Step 3: Normalize slang and abbreviations
def normalize_text(text):
    words = text.split()
    normalized_words = [normalization_dict.get(word.lower(), word) for word in words]
    return " ".join(normalized_words)

# Step 4: Fix 'h' used instead of 'x' or 'kh' when followed by vowels
def fix_h_pronunciations(text):
    return re.sub(r'\bh([aeiou])', r'kh\1', text)

# Step 5: Transliterate normalized Latin → Cyrillic
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

# Step 6: Full pipeline: Normalize → Fix 'h' → Transliterate
def latin_to_cyrillic_pipeline(text):
    if pd.isna(text):
        return ""
    text = str(text)
    text = fix_h_pronunciations(text)
    text = normalize_text(text)
    return transliterate_latin_to_cyrillic(text)

# Step 7: Process Excel file
def process_excel(input_file, output_file, latin_column):
    df = pd.read_excel(input_file)

    # Apply the transliteration pipeline
    df['cyrillic'] = df[latin_column].apply(latin_to_cyrillic_pipeline)

    # Save result to new Excel file
    df.to_excel(output_file, index=False)
    print(f"Saved: {output_file}")

# Step 8: Main
if __name__ == "__main__":
    input_excel = "D:/sentiment/Facebook Comments 1.xlsx"    # ⬅ Change to your file name
    output_excel = "D:/sentiment/output_cyrillic.xlsx"
    latin_column = "text_latin"  # ⬅ Change to your column name in the Excel file

    process_excel(input_excel, output_excel, latin_column)
