import re
from utils import is_shad

def add_shad_to_note_text(note_chunk):
    note_text = ''
    note_options = re.split("(;)", note_chunk)
    for note_option in note_options:
        if note_option != ';':
            if note_option[-1] == '>':
                note_text += f"{note_option[:-1]}།>"
            else:
                note_text += f"{note_option}།"
        else:
            note_text += ';'

    return note_text

def resolve_missing_punct_note_text(collated_text):
    reformated_collated_text = ""

    chunks = re.split('(\(\d+\) <.+?>)', collated_text)

    for chunk_walker,chunk in enumerate(chunks):
        try:
            next_chunk = chunks[chunk_walker+1]
        except:
            next_chunk = ''
        if re.search('\(\d+\) <.+?>', chunk):
            if next_chunk and is_shad(next_chunk[0]):
                reformated_collated_text += '།'
                updated_note_text = add_shad_to_note_text(chunk)
                reformated_collated_text += updated_note_text
                chunks[chunk_walker+1] = next_chunk[1:]
            else:
                reformated_collated_text += chunk
        else:
            reformated_collated_text += chunk
    return reformated_collated_text


if __name__ == "__main__":

    collated_text = 'ནཱ་མ་བྲྀཏྟི(3) <«སྡེ་»བྲིཏྟ;«སྣར་»བྲིཏྟི>། བོད་སྐད་དུ། རྒྱུ་ནི་ཡོད་པ་མ་ཡིན(4) <«སྡེ་»«སྣར་»ཡིན་ནོ>། ཅིའི་ཕྱིར་ཞེ་ན། '
    expected_text = 'ནཱ་མ་བྲྀཏྟི།(3) <«སྡེ་»བྲིཏྟ།;«སྣར་»བྲིཏྟི།> བོད་སྐད་དུ། རྒྱུ་ནི་ཡོད་པ་མ་ཡིན།(4) <«སྡེ་»«སྣར་»ཡིན་ནོ།> ཅིའི་ཕྱིར་ཞེ་ན། '

    actual_text = resolve_missing_punct_note_text(collated_text)
    print(actual_text)
    assert actual_text == expected_text


