import re


def normalize_spaces(text: str) -> str:
    """
    Removes extra spaces between words and trims the string.

    Args:
        text (str): The input string to normalize

    Returns:
        str: The string with normalized spacing
    """
    return re.sub(r"\s+", " ", text.strip())


# Define common special_s to be replaced with spaces
IGNORED_CHARS = [
    "/",
    ",",
    ";",
    "-",
    "_",
    "|",
    "\\",
    "+",
    "&",
    "(",
    ")",
    "[",
    "]",
    "{",
    "}",
    "?",
    "!",
    ".",
    " ",
]


# Normalize both strings by replacing special_s with spaces and converting to lowercase
def normalize_string(text: str, ignored_chars=IGNORED_CHARS) -> str:
    text = text.lower()
    for special_char in ignored_chars:
        text = text.replace(special_char, " ")
    return normalize_spaces(text)


def split_string(text: str, separator: str = " ") -> list[str]:
    parts = []
    for part in text.split(separator):
        part = part.strip()
        if part:
            parts.append(part)
    return parts


def get_string_common_prefix(
    a: str,
    b: str,
) -> int:
    min_len = min(len(a), len(b))
    for i in range(min_len):
        if a[i] != b[i]:
            return i
    return min_len
