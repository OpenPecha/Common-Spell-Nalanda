from common_speller import *
from utils import from_yaml
import json


def get_hfml_text(work_dir, text_id):
    has_outlier = False
    version_paths, has_outlier = get_version_paths(work_dir)
    # work_with_outliers.append(work_dir.stem)
    examplar_version_path = work_dir / '02derge.txt'
    if not examplar_version_path.exists():
        examplar_version_path = version_paths[0]
    version_paths.remove(examplar_version_path)

    common_spell_text = get_common_spell(examplar_version_path, version_paths)
    (work_dir.parent.parent.joinpath('common_spell') / f'{text_id}.txt').write_text(common_spell_text, encoding='utf-8')
    common_spell_text = (work_dir.parent.parent.joinpath('common_spell') / f'{text_id}.txt').read_text(encoding='utf-8')
    four_edition_paths = get_four_edition_paths(work_dir)
    hfml_common_spell_text = get_hfml_CS_with_cs_and_four_edition(four_edition_paths, common_spell_text)
    hfml_common_spell_text = hfml_common_spell_text.replace('\n', '')
    normalized_hfml_common_spell_text = get_normalized_text(hfml_common_spell_text)
    normalized_hfml_common_spell_text = resolve_missing_punct_note_text(normalized_hfml_common_spell_text)
    (work_dir.parent.parent.joinpath('normalized_collated') / f'{text_id}.txt').write_text(normalized_hfml_common_spell_text,encoding='utf-8')
    return normalized_hfml_common_spell_text

def get_meta_data(philo_infos, text_meta):
    metadata= {
        'title_bo': text_meta.get('text_title', ''),
        'alt_tile_bo': text_meta.get('text_alt_title', ''),
        'text_id': text_meta.get('text_id', ''),
        'author_en': philo_infos.get('philo_en_name', ''),
        'author_bo': philo_infos.get('philo_bo_name', ''),
        'bdrc_person_id': philo_infos.get('bdrc_person_id', ''),
        'initial_creation_type': 'input',
        'language': 'bo'
    }

    return metadata

def get_philo_name_mapping():
    philo_name_mapping = {}
    philo_names = Path('./pan_mapping.txt').read_text(encoding='utf-8').split('\n')
    for philo_name in philo_names:
        philo_bo_name, bdrc_person_id, philo_number, philo_en_name = philo_name.split('\t')
        philo_name_mapping[philo_number] = {
            'philo_en_name': philo_en_name,
            'bdrc_person_id': bdrc_person_id,
            'philo_bo_name': philo_bo_name
        }
    return philo_name_mapping

def get_philo_info(philo_en_name, philo_name_mapping):
    philo_info = {}
    for philo_number, philo_info in philo_name_mapping.items():
        if philo_info['philo_en_name'] == philo_en_name:
            return philo_info

def get_text_meta(text_catalog, text_uuid):
    text_meta = {}
    for text_id, text_info in text_catalog.items():
        text_gfolder_title = text_info['gfolder_text_title']
        text_alt_title = text_gfolder_title.split(' ')[1]
        if text_gfolder_title.split(' ')[0] == text_uuid:
            text_meta['text_id'] = text_id
            text_meta['text_title'] = text_info['text_title']
            text_meta['text_alt_title'] = text_alt_title
    return text_meta

def is_valid_hfml(hfml_text):
    if "><" in hfml_text:
        return False
    return True

def save_text(hfml_text, text_meta, text_id, philo_id):
    text_dir = Path(f'./hfmls/{philo_id}/{text_id}')
    text_dir.mkdir(parents=True, exist_ok=True)
    hfml_text_path = text_dir / f'{text_id}.txt'
    hfml_text_path.write_text(hfml_text, encoding='utf-8')
    meta_path = text_dir / f'{text_id}_meta.json'
    meta_path.write_text(json.dumps(text_meta, ensure_ascii=False), encoding='utf-8')

if __name__ == "__main__":
    philo_ids = ['01-Nagarjuna','02-Aryadeva','03-Buddhapalita','04-Bhavaviveka','05-Chandrakirti',
        '06-Shantideva','07-Shantarakshita','08-Kamalashila','09-Asanga','10-Vasubandhu',
        '11-Dignaga','12-Dharmakirti','13-Arya Vimuktisena','14-Haribhadra','15-Gunaprabha',
        '16-Shakyaprabha','17-Atisha',
    ]
    philo_name_mapping = get_philo_name_mapping()
    for philo_id in philo_ids[5:]:
        text_with_issue = []
        philo_work_dirs = list(Path(f'./data/{philo_id}/works/').iterdir())
        philo_work_dirs.sort()
        philo_en_name = philo_id.split('-')[1]
        philo_infos = get_philo_info(philo_en_name, philo_name_mapping)
        text_catalog = from_yaml(Path(f'./data/{philo_id}/{philo_id}_text_catalog.yml'))
        for philo_work_dir in philo_work_dirs:
            text_uuid = philo_work_dir.stem
            try:
                text_meta  = get_text_meta(text_catalog, text_uuid)
            except:
                text_meta = {}
            if text_meta.get('text_id', ''):
                try:
                    hfml_text = get_hfml_text(philo_work_dir, text_uuid)
                except:
                    text_with_issue.append(text_meta['text_id'])
                    continue
                if is_valid_hfml(hfml_text):
                    metadata = get_meta_data(philo_infos, text_meta)
                    save_text(hfml_text, metadata, text_meta['text_id'], philo_id)

                else:
                    text_with_issue.append(text_meta['text_id'])
            else:
                text_with_issue.append(text_uuid)
        Path(f'./hfmls/{philo_id}/text_with_issue.txt').write_text('\n'.join(text_with_issue), encoding='utf-8')
                
                