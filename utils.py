import re
from typing import DefaultDict
import yaml
from botok import WordTokenizer
from botok.tokenizers.chunktokenizer import ChunkTokenizer


wt = WordTokenizer()

def reformat_line_break(text):
    reformated_text = ''
    text = text.replace("\n", "")
    chunks = re.split('(། །)', text)
    walker = 1
    for chunk in chunks:
        if re.search('། །', chunk):
            if walker == 50:
                reformated_text += f"{chunk}\n"
                walker = 0
            else:
                reformated_text += chunk
                walker += 1
        else:
            reformated_text += chunk
    return reformated_text

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



def get_context(chunk, type_):
    chunk = chunk.replace(':', '')
    context = ''
    syls = get_syls(chunk)
    if len(syls) >= 4:
        if type_ == 'left':
            context = f"{''.join(syls[-4:])}"
        else:
            context = f"{''.join(syls[:4])}"
    else:
        context = chunk
    return context

def clean_note(note_text):
    noise_anns = ['«པེ་»', '«སྣར་»', '«སྡེ་»', '«ཅོ་»', '\(\d+\) ', ':']
    for noise_ann in noise_anns:
        note_text = re.sub(noise_ann, '', note_text)
    return note_text

def get_default_option(prev_chunk):
    default_option = ''
    if ':' in prev_chunk:
        default_option = re.search(':(.*)', prev_chunk,re.DOTALL).group(1)
    else:
        syls = get_syls(prev_chunk)
        if syls:
            default_option = syls[-1]
    return default_option.strip()

def get_note_options(default_option, note_chunk):
    note_chunk = re.sub('\(\d+\) ', '', note_chunk)
    z = re.match("<.+?(\(.+\))>",note_chunk)
    if z:
        note_chunk = note_chunk.replace(z.group(1),'')
    if "+" in note_chunk:
        default_option = ""
    note_chunk = re.sub("\+", "", note_chunk)
    pub_mapping = {
        '«པེ་»': 'peking',
        '«པེ»': 'peking',
        '«སྣར་»': 'narthang',
        '«སྣར»': 'narthang',
        '«སྡེ་»': 'derge',
        '«སྡེ»': 'derge',
        '«ཅོ་»': 'chone',
        '«ཅོ»': 'chone'
    }
    note_options = {
        'peking': '',
        'narthang': '',
        'derge': '',
        'chone': ''
    }
    note_parts = re.split('(«པེ་»|«སྣར་»|«སྡེ་»|«ཅོ་»|«པེ»|«སྣར»|«སྡེ»|«ཅོ»)', note_chunk)
    pubs = note_parts[1::2]
    notes = note_parts[2::2]
    for walker, (pub, note_part) in enumerate(zip(pubs, notes)):
        if note_part:
            note_options[pub_mapping[pub]] = note_part.replace('>', '')
        else:
            if notes[walker+1]:
                note_options[pub_mapping[pub]] = notes[walker+1].replace('>', '')
            else:
                note_options[pub_mapping[pub]] = notes[walker+2].replace('>', '')
    for pub, note in note_options.items():
        if "-" in note:
            note_options[pub] = ""
        if not note:
            note_options[pub] = default_option
    return note_options

def update_left_context(default_option, prev_chunk, chunk):
    left_context = re.sub(f'{default_option}$', '', prev_chunk)
    if "+" in chunk:
        left_context = prev_chunk
    return left_context

def get_alt_options(note):
    alt_options = []
    start,end = note["span"]
    real_note = note["real_note"]
    default_option = note['default_clone_option']
    note_options = note['note_options']
    for note in set(note_options.values()):
        if note.replace("\n","") != default_option and note != "":
            z = re.search(fr"»(\+|-)?{note}",real_note)
            option_start = start+z.start()+1
            option_end = start+z.end()
            alt_options.append({"note":note,"span":(option_start,option_end)})
    
    alt_options = sort_options(alt_options)
    return alt_options   


def sort_options(options):
    if len(options) == 1:
        return options
    else:
        sorted_data = sorted(options, key=lambda x: x['span'][0],reverse=True) 
    return sorted_data   

def get_note_sample(prev_chunk, note_chunk, next_chunk,collated_text,prev_end):
    default_option = get_default_option(prev_chunk)
    default_option = clean_default_option(default_option)
    prev_chunk = update_left_context(default_option, prev_chunk, note_chunk)
    prev_context = get_context(prev_chunk, type_= 'left')
    next_context = get_context(next_chunk, type_= 'right')
    note_options = get_note_options(default_option, note_chunk)
    note_options = dict(sorted(note_options.items()))
    note_span,prev_end,real_note = get_note_span(collated_text,note_chunk,prev_end)
    note = {
        "left_context":prev_context,
        "right_context":next_context,
        "default_option": default_option,
        "default_clone_option":default_option,
        "note_options":note_options,
        "span":note_span,
        "real_note":real_note
    }
    note["alt_options"] = get_alt_options(note)

    return note,prev_end

def clean_default_option(option):
    option = option.replace("\n","")
    if re.search("\d+-\d+",option):
        option = re.sub("\d+\-\d+","",option)
    return option    

def get_notes(collated_text):
    cur_text_notes = []
    prev_end = 0
    chunks = re.split('(\(\d+\) <.+?>)', collated_text)
    prev_chunk = chunks[0]
    for chunk_walker, chunk in enumerate(chunks):
        try:
            next_chunk = chunks[chunk_walker+1]
        except:
            next_chunk = ''
        if re.search('\(\d+\) <.+?>', chunk):
            note,prev_end  = get_note_sample(prev_chunk, chunk, next_chunk,collated_text,prev_end)
            cur_text_notes.append(note)
            continue
        prev_chunk = chunk
    return cur_text_notes

def get_notes_samples(collated_text, note_samples, text_id):
    collated_text = collated_text.replace('\n', '')
    collated_text = re.sub('\d+-\d+', '', collated_text)
    cur_text_notes = get_notes(collated_text)
    for cur_text_note, note_options in cur_text_notes:
        if note_samples.get(cur_text_note, {}):
            note_samples[cur_text_note]['count'] += 1
            note_samples[cur_text_note]['text_id']=text_id
        else:
            note_samples[cur_text_note] = DefaultDict()
            note_samples[cur_text_note]['count'] = 1
            note_samples[cur_text_note]['text_id']=text_id
            note_samples[cur_text_note]['note_options'] = note_options
    return note_samples

def is_all_option_same(note_options):
    if note_options['derge'] == note_options['chone'] == note_options['peking'] == note_options['narthang']:
        return True
    else:
        return False

def get_note_context(note):
    right_context = ''
    left_context = ''
    if re.search(r'(.+)\[', note):
        left_context = re.search(r'(.+)\[', note).group(1)
    if re.search(r'\](.+)', note):
        right_context = re.search(r'\](.+)', note).group(1)
    return left_context, right_context

def get_sample_entry(note_walker, note, note_info):
    all_option_same_flag = is_all_option_same(note_info.get('note_options', {}))
    left_context, right_context = get_note_context(note)
    data_entry = [
        note_walker,
        '',
        left_context,
        note_info['note_options']['derge'],
        note_info['note_options']['chone'],
        note_info['note_options']['peking'],
        note_info['note_options']['narthang'],
        right_context,
        '',
        '',
        '',
        all_option_same_flag,
        note_info['count'],
        note_info['text_id'],
        ]
    return data_entry

def is_title_note(note):
    notes_options = []
    notes_options.append(note['note_options']['chone'])
    notes_options.append(note['note_options']['derge'])
    notes_options.append(note['note_options']['narthang'])
    notes_options.append(note['note_options']['peking'])
    
    right_context = note['right_context']
    left_context = note['left_context']
    left_context = re.sub(r"\xa0", " ", left_context)
    possible_left_texts = ["༄༅། །"]
    possible_right_texts = ["༄༅༅། །རྒྱ་གར་","༄༅། །རྒྱ་གར་","༅༅། །རྒྱ་གར་སྐད་དུ།","༄༅༅། ","༄༅༅།། །རྒྱ་གར་","ལྟར་བཀོད་ཅིང།"]
    
    
    for left_text in possible_left_texts:
        if left_text in left_context:
            return True
    for right_text in possible_right_texts:
        if right_text in right_context:
            for note_option in notes_options:
                if '༄༅།' in note_option:
                    return False
                else:
                    return True
    return False

def get_note_span(collated_text,chunk,prev_end):
    p = re.compile("\(.+?\) <.*?>")
    for m in p.finditer(collated_text):
        start,end = m.span()
        if m.group() in chunk and prev_end <= start:
            return m.span(),end,m.group()


def get_default_word(collated_text, end_index, prev_end):
    if prev_end == None:
        prev_end = 0
    if end_index == 0:
        return None,None
    elif ":" in collated_text[prev_end:end_index]:
        span = collated_text[prev_end:end_index].find(":")
        colon_pos = span + prev_end + 1
        return collated_text[colon_pos:end_index],colon_pos
    else:
        index = end_index-1
        start_index = ""
        while index >= 0:
            if re.search("(\s|>)",collated_text[index]):
                index_in = end_index-2
                while collated_text[index_in] not in ["་","།",">"]:
                    index_in-=1
                start_index = index_in+1
                break
            index-=1
        default_word = collated_text[start_index:end_index].replace("\n","")
        if re.search("\d+\-\d+",default_word):
            default_word = re.sub("\d+\-\d+","",default_word)

        return default_word,start_index

        
def toyaml(dict):
    return yaml.safe_dump(dict, sort_keys=False, allow_unicode=True)

def from_yaml(yml_path):
    return yaml.safe_load(yml_path.read_text(encoding="utf-8"))

def get_default_word_start(collated_text,note):
    start_index = ""
    start,_ = note['span']
    default_option = note['default_clone_option']
    default_start = start-len(default_option)
    if collated_text[default_start-1] == ":":
        start_index = default_start-1
    else:
        start_index = default_start 
    return start_index

def get_text_id_and_vol_num(text_path):
    text_name = text_path.name[:-4]
    map = re.match(r"([A-Z][0-9]+[a-z]?)\_(v[0-9]+)",text_name)
    text_id = map.group(1)
    vol_num = map.group(2)[1:]
    return text_id, vol_num

def check_all_notes(note):
    for _, note_option in note['note_options'].items():
        if note_option == "":
            return False
        elif "!" in note_option:
            return False
    return True  


def  get_prev_note_span(notes, num):
    if num == 0:
        return None, None
    else:
        return notes[num-1]['span']



def get_tokens(text):
    tokens = wt.tokenize(text, split_affixes=False)
    return tokens


def get_option_span(note,option):
    start,end = note["span"]
    z = re.search(f"\{option}",note["real_note"])
    option_start = start+z.start()
    option_end = start+z.end()
    return option_start,option_end


def get_note_alt(note):
    note_parts = re.split('(«པེ་»|«སྣར་»|«སྡེ་»|«ཅོ་»|«པེ»|«སྣར»|«སྡེ»|«ཅོ»)',note['real_note'])
    notes = note_parts[2::2]
    options = []
    for note in notes:
        if note != "":
            options.append(note.replace(">",""))
    return options


def get_payload_span(note):
    real_note = note['real_note']
    z = re.match("(.*<)(«.*»)+(.*)>",real_note)
    start,_ = note["span"]
    pyld_start = start+len(z.group(1))+len(z.group(2))
    pyld_end = pyld_start + len(z.group(3))
    return pyld_start,pyld_end


def convert_syl_to_word(syls):
    word = ""
    for syl in syls:
        word += syl
    return word


def get_token_pos(syl):
    tokens = get_tokens(syl) 
    for token in tokens:
        return token.pos   


def is_word(word):
    if word[-1] == "།":
        word = word[:-1]
    tokens = get_tokens(word)
    if len(tokens) == 1:
        return True
    return False

def sum_up_syll(syls,dir=None):

    word = is_shad_present(syls,dir)
    if word:
        return word         
    return ""  

def is_shad_present(syls,dir):
    words = ""
    for syl in syls:
        words+=syl

    if "།" in words or " " in words:
        if dir == "left":
            if len(syls) == 1:
                return ""
            else:
                sum_word = ""
                for word in reversed(words):
                    if word == "།" or word == " ":
                        return sum_word
                    sum_word=word+sum_word
        elif dir =="right":
            if len(syls) == 1:
                return syls[0]
            else:
                sum_word=""        
                for word in words:
                    sum_word = sum_word+word
                    if word == "།":
                        return sum_word

    return words