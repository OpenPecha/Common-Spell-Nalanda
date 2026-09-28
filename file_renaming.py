from pathlib import Path

import os
from openpecha.core.ids import get_id

def rename_files(old_name, new_name):
    os.rename(old_name, new_name)



if __name__ == "__main__":
    philo_id = '01-Nagarjuna'

    file_name_map = {
        'chone.txt': '01chone.txt',
        'derge.txt': '02derge.txt',
        'narthang.txt': '03narthang.txt',
        'peking.txt': '04peking.txt',
    }
    work_dirs = list(Path(f'./data/{philo_id}/work_with_issue/').iterdir())
    mapping = ''
    # for work_dir in work_dirs:
    #     new_dir_name = get_id("", 8)
    #     mapping += f"{work_dir.name} -> {new_dir_name}\n"
    #     new_path = Path(f'./data/{philo_id}/work_with_issue/{new_dir_name}')
    #     os.rename(work_dir, new_path)
    # Path(f'./data/{philo_id}/work_with_issue/mapping.txt').write_text(mapping)
    for work_dir in work_dirs:
        text_id = work_dir.name
        text_files = list(work_dir.iterdir())
        for text_file in text_files:
            if text_file.suffix == ".txt":
                new_name = file_name_map.get(text_file.name, "")
                if not new_name:
                    print(f"Skipping {text_file}")
                    continue
                new_path = work_dir / new_name
                rename_files(text_file, new_path)
                print(f"Renamed {text_file} to {new_name}")
            else:
                print(f"Skipping {text_file}")