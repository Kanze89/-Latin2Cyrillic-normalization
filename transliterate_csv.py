import pandas as pd
import re

# Step 1: Normalization dictionary (expand as needed)
normalization_dict = {
    "bn": "baina",
    "bnu": "baina uu",
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
    "xun": "xun",  # for consistency
}

# Step 2: Latin to Cyrillic mapping
latin_to_cyrillic = {
    "ch": "ч", "sh": "ш", "ts": "ц", "ya": "я", "yo": "ё", "yu": "ю", "ee": "э",
    "a": "а", "b": "б", "c": "ц", "d": "д", "e": "е", "f": "ф", "g": "г",
    "h": "х", "i": "и", "j": "ж", "k": "к", "l": "л", "m": "м", "n": "н",
    "o": "о", "p": "п", "q": "к", "r": "р", "s": "с", "t": "т", "u": "у",
    "v": "в", "w": "в", "x": "х", "y": "й", "z": "з"
}

# Step 3: Normalize text (abbreviations and slang)
def normalize_text(text):
    words = text.split()
    normalized_words = [normalization_dict.get(word.lower(), word) for word in words]
    return " ".join(normalized_words)

# Step 4: Fix 'h' used in place of 'x' or 'kh'
def fix_h_pronunciations(text):
    # Replace 'h' at the start of a word when followed by a vowel → 'kh'
    return re.sub(r'\bh([aeiou])', r'kh\1', text)

# Step 5: Transliterate Latin → Cyrillic
def transliterate_latin_to_cyrillic(text):
    # First replace digraphs (longer first)
    digraphs = ["ch", "sh", "ts", "ya", "yo", "yu", "ee"]
    for digraph in digraphs:
        text = re.sub(digraph, latin_to_cyrillic[digraph], text, flags=re.IGNORECASE)

    result = ''
    for char in text:
        lower_char = char.lower()
        result += latin_to_cyrillic.get(lower_char, char)
    return result

# Step 6: Full pipeline function
def latin_to_cyrillic_pipeline(text):
    if pd.isna(text): return ""
    text = str(text)
    text = fix_h_pronunciations(text)
    text = normalize_text(text)
    return transliterate_latin_to_cyrillic(text)

# Step 7: Process CSV
def process_csv(input_file, output_file, latin_column):
    df = pd.read_csv(input_file)

    # Apply transliteration
    df['cyrillic'] = df[latin_column].apply(latin_to_cyrillic_pipeline)

    # Save result
    df.to_csv(output_file, index=False)
    print(f"✅ Saved: {output_file}")

# Step 8: Run the script
if __name__ == "__main__":
    input_csv = "your_input.csv"       # Replace with your file
    output_csv = "output_cyrillic.csv"
    latin_column = "text_latin"        # Replace with the actual column name

    process_csv(input_csv, output_csv, latin_column)
