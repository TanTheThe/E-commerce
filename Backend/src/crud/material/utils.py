import re
from unidecode import unidecode

def generate_slug(text: str) -> str:
    text = unidecode(text)
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')
    return text