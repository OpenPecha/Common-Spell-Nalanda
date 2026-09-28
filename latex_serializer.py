import re

from pathlib import Path
from docx_serializer import reformat_note_text

def get_text_title(text):
    try:
        title = re.search("(^.+?)༄༅༅། །རྒྱ་གར་སྐད་དུ།", text).group(1)
    except:
        title = ''
    return title

def serialize_text_to_latex(text):
    annotations = []
    def replace_annotations(match):
        annotation = match.group(1)
        note_text = reformat_note_text(annotation)
        annotations.append(annotation)
        return r"\footnote{%s}" % note_text

    serialized_text = re.sub(r'\(\d+\) <(.+?)>', replace_annotations, text)
    title = get_text_title(serialized_text)
    if title:
        serialized_text = serialized_text.replace(title, r"\chapter{%s}" % title)

    serialized_text = "\setcounter{footnote}{0} \n" + serialized_text

#     latex_template = fr"""
# \documentclass[12pt,a4paper]{{book}}
# \usepackage{{fontspec}}
# \usepackage{{titlesec}}
# \usepackage[para]{{footmisc}}
# \usepackage{{polyglossia}}
# \usepackage{{fmtcount}}
# \usepackage{{fancyhdr}}
# \usepackage[footskip=1in]{{geometry}}
# \usepackage[tracking=true,protrusion=false]{{microtype}}
# \hyphenpenalty=10000
# \exhyphenpenalty=10000
# \tolerance=1000
# \emergencystretch=3em

# \newcommand{{\ii}}{{\penalty10000{{}} །}}
# \microtypecontext{{protrusion=none}}

# % \emergencystretch=0.5em % Adjust the value as needed -- this splits ང་/།

# \setdefaultlanguage{{tibetan}}
# \newfontfamily\tibetanfont[Script=Tibetan]{{Monlam Uni Ouchan2}}

# \usepackage{{perpage}}
# \MakePerPage[1]{{footnote}} % Make footnotes restart per page

# % Format footnotes in a single line
# \renewcommand{{\footnoterule}}{{\vspace{{0.3em}}\noindent\rule{{\linewidth}}{{0.5pt}}\vspace{{0.5em}}}}

# % Define header layout using fancyhdr
# \fancyhead{{}} % Clear all header fields
# \fancyhead[LE,RO]{{\thepage}}
# \fancyhead[RE]{{\leftmark}}
# \fancyhead[LO]{{\rightmark}}
# \renewcommand{{\chaptermark}}[1]{{\markboth{{#1}}{{}}}} % <-- redefined this line

# % Redefine chapter format
# \titleformat{{\chapter}}[display]
# {{\normalfont\huge\bfseries}}{{}}{{0pt}}{{\Huge}}
# \setlength{{\headheight}}{{15.80878pt}}
# \addtolength{{\topmargin}}{{-3.80878pt}}

# \pagestyle{{fancy}}

# % Override footnote numbering
# \makeatletter
# \def\@makefnmark{{\hbox{{\@textsuperscript{{\normalfont\arabic{{footnote}}}}}}}}
# \makeatother

# \begin{{document}}
# {serialized_text}
# \end{{document}}
# """

    return serialized_text



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
    for philo_id in philo_ids:

        normalized_text_paths = list(Path(f'./data/{philo_id}/normalized_collated').iterdir())
        normalized_text_paths.sort()
        for normalized_text_path in normalized_text_paths:
            # if normalized_text_path.stem == '79229AB4':
            normalized_text = normalized_text_path.read_text(encoding='utf-8')
            serialized_text = serialize_text_to_latex(normalized_text)
            Path(f'./data/latex/{philo_id}/{normalized_text_path.stem}.tex').write_text(serialized_text, encoding='utf-8')
            
    # normalized_text = Path('./normalized.txt').read_text(encoding='utf-8')
    # serialized_text = serialize_text_to_latex(normalized_text)
    # Path('./test.tex').write_text(serialized_text, encoding='utf-8')