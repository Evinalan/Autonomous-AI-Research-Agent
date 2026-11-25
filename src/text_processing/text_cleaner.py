
import re
import unicodedata


def clean_text(text):
    """
    Clean extracted research paper text while preserving
    paragraph boundaries.
    """

    if not text:
        return ""

    # Normalize unusual Unicode characters
    text = unicodedata.normalize("NFKC", str(text))

    # Fix words split across lines, such as:
    # deep learn-
    # ing -> deep learning
    text = re.sub(r"-\s*\n\s*", "", text)

    # Replace tabs and repeated spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove unwanted control characters
    text = "".join(
        character
        for character in text
        if character in "\n\r\t" or unicodedata.category(character)[0] != "C"
    )

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove spaces at the beginning and end of each line
    lines = [line.strip() for line in text.split("\n")]

    text = "\n".join(lines)

    # Reduce excessive blank lines while preserving paragraphs
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
