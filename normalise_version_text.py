import re

from pathlib import Path


def rm_space_after_double_shad(text):
    text = re.sub(r'། ། ', '། །', text)
    text = re.sub(r'།།  །། ', '།།  །།', text)
    return text

def rm_space_before_double_shad(text):
    text = re.sub(r' ། །', '། །', text)
    text = re.sub(r' །།  །།', '།།  །།', text)
    return text

def normalise_zhi_shad(text):
    text = re.sub(r'། ། ། །', '།།  །།', text)
    text = re.sub(r'། ། །།', '།།  །།', text)
    text = re.sub(r'། །། །', '།།  །།', text)
    text = re.sub(r'།། ། །', '།།  །།', text)
    text = re.sub(r'།། །།', '།།  །།', text)
    text = re.sub(r'། ། །', '།།  །།', text)
    return text

def rm_tseg_after_namje(text):
    return re.sub('(་.+ཿ)་', '\g<1>', text)

def add_space_after_single_shad(text):
    return re.sub(r'([^ |།])།([^\s])', '\g<1>། \g<2>', text)

def add_tseg_after_ngo(text):
    return re.sub(r'ངོ།', 'ངོ་།', text)

def replace_archic_word(text):
    return re.sub('\{\S+?\,(\S+?)\}', '\g<1>', text)

def rm_space_after_tseg(text):
    return re.sub(r'་ +', '་', text)


def normalise_version_text(text):
    text = add_space_after_single_shad(text)
    text = normalise_zhi_shad(text)
    text = rm_space_after_double_shad(text)
    text = rm_space_before_double_shad(text)
    text = rm_tseg_after_namje(text)
    text = add_tseg_after_ngo(text)
    text = replace_archic_word(text)
    text = rm_space_after_tseg(text)
    
    return text

def test_normalise_version_text():
    test = """
གཡས་པའི་ཕྱག་ན་ཁ་ཊྭཱཾ་ག་དངོ་། དགྲ་སྟ་འོ།རྡོ་རྗེ་འཛིན་པ། 
འོད་ཟེར་འབར་བའི་ཕྲེང་བ་ཅན།རང་བཞིན་གྱི་རྡོ་རྗེ་བསྒོམ་མོ། ། །དེ་ནས་ཨོཾ་ཡོ་ག་ཤུདྡྷཿ་སརྦ་
རྨཱ་ཡོ་ག་ཤུདྡྷོ྅ཧཾ། ། རྡོ་རྗེ་གསོར་ལ ། །ཨོཾ་ཛྙཱ་ན་ཀ་ཡོ་ཨ་ཧཾ་ཞེས་ང་རྒྱལ་བྱའོ། །། །དེ་ནས་ལག་པ་གཡོན་
པའི་མཐེའུ་ཆུང་དང་། ། ། །མཐེ་བོང་སྦྱར་ཏེ།
"""
    expected = """
གཡས་པའི་ཕྱག་ན་ཁ་ཊྭཱཾ་ག་དངོ་། དགྲ་སྟ་འོ། རྡོ་རྗེ་འཛིན་པ། 
འོད་ཟེར་འབར་བའི་ཕྲེང་བ་ཅན། རང་བཞིན་གྱི་རྡོ་རྗེ་བསྒོམ་མོ།།  །།དེ་ནས་ཨོཾ་ཡོ་ག་ཤུདྡྷཿསརྦ་
རྨཱ་ཡོ་ག་ཤུདྡྷོ྅ཧཾ། །རྡོ་རྗེ་གསོར་ལ། །ཨོཾ་ཛྙཱ་ན་ཀ་ཡོ་ཨ་ཧཾ་ཞེས་ང་རྒྱལ་བྱའོ།།  །།དེ་ནས་ལག་པ་གཡོན་
པའི་མཐེའུ་ཆུང་དང་།།  །།མཐེ་བོང་སྦྱར་ཏེ།
"""
    
    output = normalise_version_text(test)
    print(output)
    assert output == expected
    print("Test passed")

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
    philo_ids = ['08-Kamalashila']
    for philo_id in philo_ids:
        philo_work_dirs = list(Path(f'./data/{philo_id}/works/').iterdir())
        for work_dir in philo_work_dirs:
            text_id = work_dir.name
            if text_id in ["3C44070B",]:
                text_files = list(work_dir.iterdir())
                text_files.sort()
                for text_file in text_files:
                    text = text_file.read_text()
                    text = normalise_version_text(text)
                    text_file.write_text(text)
        print(f"{philo_id} done")