import pandas as pd
import re

# Step 1: Normalization dictionary
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
}

# Step 2: Latin to Cyrillic map
latin_to_cyrillic = {
    "ch": "ч", "sh": "ш", "ts": "ц", "ya": "я", "yo": "ё", "yu": "ю", "ee": "э",
    "a": "а", "b": "б", "c": "ц", "d": "д", "e": "е", "f": "ф", "g": "г",
    "h": "х", "i": "и", "j": "ж", "k": "к", "l": "л", "m": "м", "n": "н",
    "o": "о", "p": "п", "q": "к", "r": "р", "s": "с", "t": "т", "u": "у",
    "v": "в", "w": "в", "x": "кс", "y": "й", "z": "з"
}

# Step 3: Normalization function
def normalize_text(text):
    words = text.split()
    normalized_words = [normalization_dict.get(word.lower(), word) for word in words]
    return " ".join(normalized_words)

# Step 4: Transliteration function
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

# Step 5: Combined pipeline
def latin_to_cyrillic_pipeline(text):
    if pd.isna(text): return ""
    text = str(text)
    normalized = normalize_text(text)
    return transliterate_latin_to_cyrillic(normalized)

# Step 6: Load, process, and save CSV
def process_csv(input_file, output_file, latin_column):
    df = pd.read_csv(input_file)

    # Apply to column (change 'latin_column' if needed)
    df['cyrillic'] = df[latin_column].apply(latin_to_cyrillic_pipeline)

    # Save result
    df.to_csv(output_file, index=False)
    print(f"✅ Saved: {output_file}")

# ==== Example Usage ====
if __name__ == "__main__":
    input_csv = "your_input.csv"       # Replace with your file
    output_csv = "output_cyrillic.csv"
    latin_column = "text_latin"        # Change to match your column name

    process_csv(input_csv, output_csv, latin_column)
