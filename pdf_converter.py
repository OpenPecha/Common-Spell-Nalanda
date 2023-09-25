import pypandoc
import os

def convert_latex_to_docx(input_file: str, output_file: str):
    # Convert LaTeX to docx using pandoc
    output = pypandoc.convert_file(input_file, 'pdf', outputfile=output_file)
    assert output == ""

# Provide the name of your input LaTeX file and desired output docx file
input_file = "test.tex"
output_file = "output.pdf"

convert_latex_to_docx(input_file, output_file)

print(f"{input_file} has been converted to {output_file}")