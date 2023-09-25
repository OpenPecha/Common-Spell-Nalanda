import re
from pathlib import Path

from CommonSpell.encoder import Encoder
from CommonSpell.bo.tokenizer_bo import TibetanTokenizer, TibetanNormalizer
from CommonSpell.aligners.fdmp import FDMPaligner
from CommonSpell.input_filters.pattern_filter import PatternInputFilter
from CommonSpell.weighers.matrix_weigher import TokenMatrixWeigher
from CommonSpell.weighers.token_weigher_count import TokenCountWeigher
from CommonSpell.serializers.hfml import HFMLSerializer
from CommonSpell.serializers.plain_text import PlainTextSerializer
from CommonSpell.commonspeller import CommonSpeller

from openpecha.utils import dump_yaml

from normalize_note import get_normalized_text
from docx_serializer import creat_docx_footnotes_at_end_of_page
from resolve_missing_punct_note import resolve_missing_punct_note_text
# from nltk.metrics import edit_distance

# def calculate_similarity(text1, text2):
#     # Calculate the Levenshtein distance
#     distance = edit_distance(text1, text2)
#     # Calculate the similarity score
#     max_length = max(len(text2), len(text1))
#     similarity = 1 - (distance / max_length)
#     return similarity
def is_outlier(text_version, examplar_version):
    len_diff = abs(len(text_version) - len(examplar_version))
    similarity = 1-(len_diff/len(examplar_version))
    if similarity < 0.9:
        return True
    return False


def get_encoded_version_text(version_text, tokenizer, encoder):
    encoded_str = ''
    for m in tokenizer.token_pattern.finditer(version_text):
        token_s = tokenizer.normalizer.normalize_always(m.group(0))
        token_s_for_diff = tokenizer.normalizer.normalize_pre_token_diff(token_s)
        code_str, code_str_len = encoder.encode_str(token_s_for_diff)
        encoded_str += code_str
    return encoded_str

def filter_outlier_texts(version_paths, examplar_text):
    has_outlier = False
    for version_path in version_paths:
        if version_path.suffix == '.txt' and version_path.stem != '02derge':
            version_text = version_path.read_text(encoding='utf-8')
            if is_outlier(version_text, examplar_text):
                version_paths.remove(version_path)
                has_outlier = True
    return version_paths, has_outlier

def get_version_paths(version_dir):
    try:
        version_paths = list(version_dir.glob('*.txt'))
    except:
        print("witness directory doesn't exist")
        return None
    version_paths.sort()
    try:
        examplar_version_text = (version_dir / "02derge.txt").read_text(encoding='utf-8')
    except:
        examplar_version_text = version_paths[0].read_text(encoding='utf-8')
    version_paths, has_outlier = filter_outlier_texts(version_paths, examplar_version_text)
    return version_paths, has_outlier


def get_common_spell(examplar_version_path, version_paths):
    filter_patterns = [
        (re.compile('༌'), '་'),
        (re.compile('ག། །'), 'ག །'),
        (re.compile('།།'), '། །'),
        (re.compile('་།'), '།'),
        (re.compile('ང།'), 'ང༌།'),
        (re.compile('ང་།'), 'ང༌།'),
        (re.compile('་ +'), '་'),
        (re.compile('་+'), '་'),
        (re.compile('\n'), ''),
        (re.compile('། ། ། །'), '།། །།'),
        
        ]
    common_speller = CommonSpeller(FDMPaligner(), 
                                   filter_patterns, 
                                   TibetanTokenizer(Encoder(), 
                                    TibetanNormalizer(keep_eol=False)), 
                                    version_paths=version_paths, 
                                    examplar_version_path=examplar_version_path)
    
    token_matrix = common_speller.get_common_spell_matrix()
    tokenMatrixWeigher = TokenMatrixWeigher()
    weighers = [TokenCountWeigher()]

    for weigher in weighers:
        tokenMatrixWeigher.add_weigher(weigher, weigher_weight=1)
    weighted_matrix = tokenMatrixWeigher.get_weight_matrix(token_matrix)
    version_paths = [examplar_version_path] + version_paths

    plain_text_serializer = PlainTextSerializer(weighted_token_matrix=weighted_matrix,
                                                output_dir=None,
                                                text_id='',)
    
    common_spell_text = plain_text_serializer.serialize_matrix()
    return common_spell_text

def add_version(version_text, filter_patterns, tokenizer):
    for filter_pattern in filter_patterns:
        version_text = PatternInputFilter(version_text, filter_pattern[0], filter_pattern[1])
    
    token_string, token_list = tokenizer.tokenize(version_text)
    return token_string, token_list

def get_common_spell_matrix(four_edition_paths, common_spell_text, filter_patterns, tokenizer, aligner):
    token_strings = []
    token_lists = []
    token_string, token_list = add_version(common_spell_text, filter_patterns, tokenizer)
    token_strings.append(token_string)
    token_lists.append(token_list)
    for version_path in four_edition_paths:
        version_text = version_path.read_text(encoding='utf-8')
        token_string, token_list = add_version(version_text, filter_patterns, tokenizer)
        token_strings.append(token_string)
        token_lists.append(token_list)

    token_matrix = aligner.get_alignment_matrix(token_strings, token_lists)
    return token_matrix
    

def get_hfml_CS_with_cs_and_four_edition(four_edition_paths, common_spell_text):
    filter_patterns = [
        (re.compile('༌'), '་'),
        (re.compile('ག། །'), 'ག །'),
        (re.compile('།།'), '། །'),
        (re.compile('་།'), '།'),
        (re.compile('ང།'), 'ང༌།'),
        (re.compile('ང་།'), 'ང༌།'),
        (re.compile('་ +'), '་'),
        (re.compile('་+'), '་'),
        (re.compile('\n'), ''),
        (re.compile('། ། ། །'), '།། །།'),
        # (re.compile(' །'), ' །​'),
        
        ]
    aligner = FDMPaligner() 
    tokenizer = TibetanTokenizer(Encoder(), TibetanNormalizer(keep_eol=False))
    token_matrix = get_common_spell_matrix(four_edition_paths, common_spell_text, filter_patterns, tokenizer, aligner)
    tokenMatrixWeigher = TokenMatrixWeigher()
    weighers = [TokenCountWeigher()]
    versions_to_serialize = {
        '01chone': '«ཅོ་»',
        '02derge': '«སྡེ་»',
        '03narthang': '«སྣར་»',
        '04peking': '«པེ་»',
        }

    for weigher in weighers:
        tokenMatrixWeigher.add_weigher(weigher, weigher_weight=1)
    weighted_matrix = tokenMatrixWeigher.get_weight_matrix(token_matrix)
    version_paths = [Path('./common_spell.txt')] + four_edition_paths

    hfml_serializer = HFMLSerializer(weighted_token_matrix=weighted_matrix,
                                                output_dir=None,
                                                text_id='',
                                                version_paths=version_paths,
                                                verions_to_serialize=versions_to_serialize)
    hfml_common_spell_text = hfml_serializer.serialize_matrix()
    return hfml_common_spell_text

def get_four_edition_paths(work_dir):
    four_edition_paths = []
    version_paths = list(work_dir.iterdir())
    for version_path in version_paths:
        if version_path.stem in ['01chone', '02derge', '03narthang', '04peking']:
            four_edition_paths.append(version_path)
    four_edition_paths.sort()
    return four_edition_paths

def get_work_collated_docx(work_dir, text_id, docx_dir):
    has_outlier = False
    version_paths, has_outlier = get_version_paths(work_dir)
    work_with_outliers.append(version_dir.stem)
    examplar_version_path = version_dir / '02derge.txt'
    if not examplar_version_path.exists():
        examplar_version_path = version_paths[0]
    version_paths.remove(examplar_version_path)

    common_spell_text = get_common_spell(examplar_version_path, version_paths)
    (work_dir.parent.parent.joinpath('common_spell') / f'{text_id}.txt').write_text(common_spell_text, encoding='utf-8')
    # common_spell_text = (work_dir.parent.parent.joinpath('common_spell') / f'{text_id}.txt').read_text(encoding='utf-8')
    # four_edition_paths = get_four_edition_paths(work_dir)
    # hfml_common_spell_text = get_hfml_CS_with_cs_and_four_edition(four_edition_paths, common_spell_text)
    # hfml_common_spell_text = hfml_common_spell_text.replace('\n', '')
    # # Path('./hfml.txt').write_text(hfml_common_spell_text, encoding='utf-8')
    # normalized_hfml_common_spell_text = get_normalized_text(hfml_common_spell_text)
    # # Path('./normalized.txt').write_text(normalized_hfml_common_spell_text, encoding='utf-8')
    # normalized_hfml_common_spell_text = resolve_missing_punct_note_text(normalized_hfml_common_spell_text)
    # # Path('./normalized.txt').write_text(normalized_hfml_common_spell_text, encoding='utf-8')
    # collated_docx = creat_docx_footnotes_at_end_of_page(text_id, normalized_hfml_common_spell_text, docx_dir)
    
    # print(f'common spell for {version_dir.stem} is done')
    return has_outlier

    
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
    ]
    for philo_id in philo_ids[:1]:
    #དེ་ལ་འཇུག་པ་ནི་དེ་ལ་བགྲོད་པ་སྟེ། གཉིས་གཉིས་སྤྲོད་
        work_with_outliers = []
        text_with_issue = []
        philo_work_dirs = list(Path(f'./data/{philo_id}/works/').iterdir())
        # philo_work_dirs = [Path('./test')]
        Path(f'./data/{philo_id}/work_collated_docx').mkdir(parents=True, exist_ok=True)
        Path(f'./data/{philo_id}/common_spell').mkdir(parents=True, exist_ok=True)
        docx_dir = Path(f'./data/{philo_id}/work_collated_docx/')
        philo_work_dirs.sort()
        for version_dir in philo_work_dirs:
            text_id = version_dir.stem
            # if text_id == "E5D29E4E":
            print(f'working on {text_id}')
            try:
                has_outlier = get_work_collated_docx(version_dir, text_id, docx_dir)
                if has_outlier:
                    work_with_outliers.append(text_id)
            except:
                text_with_issue.append(text_id)
            
            
        dump_yaml(work_with_outliers, Path(f'./data/{philo_id}/work_with_outliers.yaml'))
        dump_yaml(text_with_issue, Path(f'./data/{philo_id}/text_with_issue.yaml'))