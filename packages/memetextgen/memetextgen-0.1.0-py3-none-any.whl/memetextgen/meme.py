# memegen/meme.py

import random

def to_meme_case(text):
    """
    Converts a string to meme-case by randomly switching letter cases.
    
    Example:
        "hello world" → "HeLLo WoRLd"
    """
    return ''.join(random.choice([c.lower(), c.upper()]) for c in text)
