import os
import re
from pathlib import Path

from docx import Document
from docx.shared import Pt
from pypandoc import convert_text


def split_text(content):

    chunks = re.split(r"(\(\d+\) <.+?>)", content)

    return chunks


def parse_collated_text(collated_text):
    note_walker = 1
    collated_text_md = ""
    chunks = split_text(collated_text)
    for chunk in chunks:
        if chunk and re.search(r"\(\d+\) <.+?>", chunk):
            collated_text_md += f"[^{note_walker}]"
            note_walker += 1
        else:
            collated_text_md += chunk
    collated_text_md = collated_text_md + '\n\n'
    return collated_text_md


def reformat_namgyal_non_format(notes):
    reformated_note_text = ""
    for pub, note in notes.items():
        reformated_note_text += f"{note} {pub}"
    full_names = {
        "«སྡེ་»": "སྡེ་དགེ།",
        "«ཅོ་»": "ཅོ་ནེ།",
        "«པེ་»": "པེ་ཅིན།",
        "«སྣར་»": "སྣར་ཐང་།",
    }
    for tib_abv, full_name in full_names.items():
        reformated_note_text = reformated_note_text.replace(tib_abv, f" {full_name} ")
    return reformated_note_text



def reformat_note_text(note_text):
    reformated_note_text = ""
    note_parts = re.split("(«.+?»)", note_text)
    notes = {}
    cur_pub = ""
    for note_part in note_parts[1:]:
        if note_part:
            if "«" in note_part:
                cur_pub += note_part
            else:
                notes[cur_pub] = note_part
                cur_pub = ""
    reformated_note_text = reformat_namgyal_non_format(notes)
    return reformated_note_text


def reformat_title_note_text(note_text):
    """Reformat the title note text

    Args:
        note_text (str): note text
        lang (str): languange code

    Returns:
        str: reformated title note text
    """
    reformated_note_text = note_text
    abv_replacement = {
        "«སྡེ་»": "སྡེ་དགེ།",
        "«ཅོ་»": "ཅོ་ནེ།",
        "«པེ་»": "པེ་ཅིན།",
        "«སྣར་»": "སྣར་ཐང་།",
    }
    for abv, abv_alt in abv_replacement.items():
        reformated_note_text = reformated_note_text.replace(abv, f"{abv_alt}")
    return reformated_note_text


def parse_note(collated_text):
    note_md = "\n"
    notes = re.finditer(r"\((\d+)\) <(.+?)>", collated_text)
    for note_walker, note in enumerate(notes, 1):
        note_text = reformat_note_text(note.group(2))
        note_md += f"[^{note_walker}]: {note_text}\n"
    return note_md


def creat_docx_footnotes_at_end_of_page(text_id, collated_text, path):
    collated_text_md_nam = ""
    collated_text_md_nam = parse_collated_text(collated_text)
    collated_text_md_nam += parse_note(collated_text)
    output_path_nam = path / f"{text_id}_format_namgyal.docx"
    convert_text(
        collated_text_md_nam, "docx", "markdown", outputfile=str(output_path_nam)
    )
    return output_path_nam



if __name__ == "__main__":
    collated_text = Path('./test/test_normalized.txt').read_text(encoding='utf-8')
    text_id = 'test'
    path = Path('./test')
    creat_docx_footnotes_at_end_of_page(text_id, collated_text, path)