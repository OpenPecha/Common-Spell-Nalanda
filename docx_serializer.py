import os
import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION_START
from docx.shared import Inches, Pt
from docx.enum.text import WD_LINE_SPACING
from pypandoc import convert_text
from botok import WordTokenizer
from botok.tokenizers.chunktokenizer import ChunkTokenizer


def split_text(content):

    chunks = re.split(r"(\(\d+\) <.+?>)", content)

    return chunks


def parse_collated_text(collated_text):
    note_walker = 1
    collated_text_md = ""
    chunks = split_text(collated_text)
    for chunk in chunks:
        chunk = chunk.replace(":", "")
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
        reformated_note_text += f"༼{pub}༽ {note} "
    full_names = {
        "«སྡེ་»": "སྡེ།",
        "«ཅོ་»": "ཅོ།",
        "«པེ་»": "པེ།",
        "«སྣར་»": "སྣར།",
    }
    for tib_abv, full_name in full_names.items():
        reformated_note_text = reformated_note_text.replace(tib_abv, f"{full_name} ")

    reformated_note_text = reformated_note_text.replace(" ༽", "༽")
    reformated_note_text = reformated_note_text.replace("༼ ", "༼")
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

def is_shad(text):
    shads = ['། །', '།', '།།', '། ']
    if text in shads:
        return True
    return False

def get_syls(text):
    tokenizer = ChunkTokenizer(text)

    tokens = tokenizer.tokenize()
    syls = []
    syl_walker = 0
    for token in tokens:
        token_string = token[1]
        if is_shad(token_string):
            try:
                syls[syl_walker-1] += token_string
            except:
                syls.append(token_string)
                syl_walker += 1
        else:
            syls.append(token_string)
            syl_walker += 1
    return syls

def get_default_note_text(chunk):
    if ":" in chunk:
        return re.search(":(.+)", chunk).group(1)
    else:
        syls = get_syls(chunk)
        if syls:
            return syls[-1]
        else:
            return ""


def parse_note(collated_text):
    note_md = "\n"
    chunks = split_text(collated_text)
    note_walker = 1
    prev_chunk = chunks[0]
    for chunk in chunks:
        if chunk and re.search(r"\(\d+\) <.+?>", chunk):
            default_note = get_default_note_text(prev_chunk)
            collated_note = re.search(r"\(\d+\) <(.+?)>", chunk).group(1)
            note_text = reformat_note_text(collated_note)
            note_md += f"[^{note_walker}]: {default_note} {note_text}\n"
            note_walker += 1
        prev_chunk = chunk
    # notes = re.finditer(r"\((\d+)\) <(.+?)>", collated_text)
    # for note_walker, note in enumerate(notes, 1):
    #     note_text = reformat_note_text(note.group(2))
    #     note_md += f"[^{note_walker}]: {note_text}\n"
    return note_md

def reformat_page_layout(docx_path):
    doc = Document(docx_path)
    for section in doc.sections:
        section.page_width = Inches(6.75)
        section.page_height = Inches(9.5)
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(1)
        section.right_margin = Inches(0.75)
    doc.save(docx_path)
    

def resize_font(docx_path):
    

    # Load the existing DOCX file
    doc = Document(docx_path)

    # Set the font size for the body text (14 points)
    body_font_size = Pt(16)

    # Iterate through the document to reformat the text
    for paragraph in doc.paragraphs:
        # Body text paragraph, change font size to 14 points
        for run in paragraph.runs:
            font = run.font
            font.size = body_font_size
        paragraph.paragraph_format.line_spacing = 2

    

    # Save the modified DOCX file
    doc.save(docx_path)

def creat_docx_footnotes_at_end_of_page(text_id, collated_text, path):
    collated_text_md_nam = ""
    collated_text_md_nam = parse_collated_text(collated_text)
    collated_text_md_nam += parse_note(collated_text)
    output_path_nam = path / f"{text_id}_format_namgyal.docx"
    convert_text(
        collated_text_md_nam, "docx", "markdown", outputfile=str(output_path_nam), extra_args=['+RTS', '-K512M', '-RTS', '--variable', 'fontsize=14']
    )
    reformat_page_layout(output_path_nam)
    resize_font(output_path_nam)
    return output_path_nam



if __name__ == "__main__":
    philo_ids = [
        '01-Nagarjuna',
        '02-Aryadeva',
        '03-Buddhapalita',
        '04-Bhavaviveka',
        '05-Chandrakirti',
        '06-Shantideva',
        '07-Shantarakshita',
        '08-Kamalashila',
        '09-Asanga',
        '10-Vasubandhu',
        '11-Dignaga',
        '12-Dharmakirti',
        '13-Arya Vimuktisena',
        '14-Haribhadra',
        '15-Gunaprabha',
        '16-Shakyaprabha',
        '17-Atisha',
        'test'
    ]
    for philo_id in philo_ids[-1:]:
        philo_work_dirs = list(Path(f'./data/{philo_id}/works/').iterdir())
        docx_dir = Path(f'./data/{philo_id}/work_collated_docx/')
        philo_work_dirs.sort()
        for version_dir in philo_work_dirs:
            text_id = text_id = version_dir.stem
            collated_text = Path(f'./data/{philo_id}/normalized_collated/{text_id}.txt').read_text(encoding='utf-8')
            normalised_collated_text = remove_empty_notes(collated_text)
            creat_docx_footnotes_at_end_of_page(text_id, collated_text, docx_dir)