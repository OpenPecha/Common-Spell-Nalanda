from pathlib import Path
import json

from botok.chunks.chunks import TokChunks


def get_syllables(string):
    tok_chunks = TokChunks(string)
    syls = tok_chunks.get_syls()
    return syls

def get_syllable_count(string):
    syllables = get_syllables(string)
    return len(syllables)


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

    philo_datas = {}

    for philo_id in philo_ids:
        cur_philo_syllable_count = 0
        cur_philo_work_count = 0
        philo_text_list = Path(f'./data/{philo_id}/{philo_id}_text_id_title.txt').read_text().split('\n')
        philo_datas[philo_id] = len(philo_text_list)

        # common_spell_dir = Path(f'./data/{philo_id}/common_spell')
        # common_spell_file_paths = list(common_spell_dir.iterdir())
        # # for common_spell_file_path in common_spell_file_paths:
        # #     common_spell_text = common_spell_file_path.read_text()
        # #     syllable_count = get_syllable_count(common_spell_text)
        # #     cur_philo_syllable_count += syllable_count
        
        # # philo_datas[philo_id]['syllable_count'] = cur_philo_syllable_count
        # philo_datas[philo_id] = len(common_spell_file_paths)
    json.dump(philo_datas, open('./data/philo_work_count.json', 'w'), indent=2)