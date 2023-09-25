import re

from pathlib import Path

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
        annotations.append(annotation)
        return r"\footnote{%s}" % annotation

    serialized_text = re.sub(r'\(\d+\) <(.+?)>', replace_annotations, text)
    title = get_text_title(serialized_text)
    serialized_text = serialized_text.replace(title, r"\chapter{%s}" % title)

    latex_template = fr"""
\documentclass[12pt,a4paper]{{book}}
\usepackage{{fontspec}}
\usepackage{{titlesec}}
\usepackage[para]{{footmisc}}
\usepackage{{polyglossia}}
\usepackage{{fmtcount}}
\usepackage{{fancyhdr}}
\usepackage[footskip=1in]{{geometry}}
\usepackage[tracking=true,protrusion=false]{{microtype}}
\hyphenpenalty=10000
\exhyphenpenalty=10000
\tolerance=1000
\emergencystretch=3em

\newcommand{{\ii}}{{\penalty10000{{}} །}}
\microtypecontext{{protrusion=none}}

% \emergencystretch=0.5em % Adjust the value as needed -- this splits ང་/།

\setdefaultlanguage{{tibetan}}
\newfontfamily\tibetanfont[Script=Tibetan]{{Monlam Uni Ouchan2}}

\usepackage{{perpage}}
\MakePerPage[1]{{footnote}} % Make footnotes restart per page

% Format footnotes in a single line
\renewcommand{{\footnoterule}}{{\vspace{{0.3em}}\noindent\rule{{\linewidth}}{{0.5pt}}\vspace{{0.5em}}}}

% Define header layout using fancyhdr
\fancyhead{{}} % Clear all header fields
\fancyhead[LE,RO]{{\thepage}}
\fancyhead[RE]{{\leftmark}}
\fancyhead[LO]{{\rightmark}}
\renewcommand{{\chaptermark}}[1]{{\markboth{{#1}}{{}}}} % <-- redefined this line

% Redefine chapter format
\titleformat{{\chapter}}[display]
{{\normalfont\huge\bfseries}}{{}}{{0pt}}{{\Huge}}
\setlength{{\headheight}}{{15.80878pt}}
\addtolength{{\topmargin}}{{-3.80878pt}}

\pagestyle{{fancy}}

% Override footnote numbering
\makeatletter
\def\@makefnmark{{\hbox{{\@textsuperscript{{\normalfont\arabic{{footnote}}}}}}}}
\makeatother

\begin{{document}}
{serialized_text}
\end{{document}}
"""

    return latex_template



if __name__ == "__main__":
    text = Path('./normalized.txt').read_text(encoding='utf-8')
    latex = serialize_text_to_latex(text)
    Path('./test.tex').write_text(latex, encoding='utf-8')