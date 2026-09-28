import re

from pathlib import Path

def has_improper_note(text):
    if re.search(r'»>', text):
        return True
    elif re.search(r'»«', text):
        return False

if __name__ == "__main__":
    improper_text_dir = Path('./data/improper_collated_text')
    proper_text_dir = Path('./data/proper_collated_text')
    text_dir = list(Path('./data/All_collated').iterdir())
    text_dir.sort()
    for text_path in text_dir:
        text = text_path.read_text(encoding='utf-8')

        if has_improper_note(text):
            improper_text_path = improper_text_dir / text_path.name
            improper_text_path.write_text(text, encoding='utf-8')
        else:
            proper_text_path = proper_text_dir / text_path.name
            proper_text_path.write_text(text, encoding='utf-8')

            