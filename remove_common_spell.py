import shutil

from pathlib import Path

def delete_common_spell(path):
    try:
        # Use shutil.rmtree() to remove the folder and its contents
        shutil.rmtree(path)
        print(f"Folder '{path}' and its contents have been deleted successfully.")
    except Exception as e:
        print(f"Error while deleting folder: {e}")
    
if __name__ == "__main__":
    philo_works = list(Path('./data/01-Nagarjuna/works').iterdir())
    for work in philo_works:
        if (work / 'common_spell').exists():
            delete_common_spell(work / 'common_spell')