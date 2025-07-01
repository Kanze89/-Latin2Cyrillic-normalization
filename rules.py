# rules.py

latin_exclusions = {
    "univision", "unuvision", "univishion", "voo", "skymedia",
    "mobinet", "unitel", "computer", "windows xp", "uni"
}

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
    "ym": "yum", "yum": "юм",
    "tuv": "töv", "tuw": "töv"
}

latin_to_cyrillic = {
    "ui": "уй", "vi": "үй", "üi": "үй", "ai": "ай", "ii": "ий", "kh": "х",
    "ch": "ч", "sh": "ш", "ts": "ц", "ya": "я", "yo": "ё", "yu": "ю", "ee": "ээ",
    "ö": "ө", "ü": "ү",
    "a": "а", "b": "б", "c": "ц", "d": "д", "e": "е", "f": "ф", "g": "г",
    "h": "х", "i": "и", "j": "ж", "k": "к", "l": "л", "m": "м", "n": "н",
    "o": "о", "p": "п", "q": "к", "r": "р", "s": "с", "t": "т", "u": "у",
    "v": "в", "w": "в", "x": "х", "y": "й", "z": "з"
}

digraphs = ["kh", "üi", "vi", "ui", "ai", "ii", "ch", "sh", "ts", "ya", "yo", "yu", "ee"]
