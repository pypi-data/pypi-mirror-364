# memegen/__main__.py

import sys
from .meme import to_meme_case

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m memegen 'your text here'")
        return

    input_text = ' '.join(sys.argv[1:])
    print(to_meme_case(input_text))

if __name__ == "__main__":
    main()
