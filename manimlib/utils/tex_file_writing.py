import os
import hashlib

from manimlib.constants import TEX_DIR
from manimlib.constants import TEX_TEXT_TO_REPLACE
from manimlib.constants import TEX_USE_CTEX


def tex_hash(expression, template_tex_file_body):
    id_str = str(expression + template_tex_file_body)
    hasher = hashlib.sha256()
    hasher.update(id_str.encode())
    # Truncating at 16 bytes for cleanliness
    return hasher.hexdigest()[:16]

## Since dvisvgm 2.6.2 added pdf support,
## *.tex -> *.pdf -> *.svg should be more helpful.

def tex_to_svg_file(expression, template_tex_file_body):
    tex_file = generate_tex_file(expression, template_tex_file_body)
    pdf_file = tex_to_pdf(tex_file)
    return pdf_to_svg(pdf_file)

def generate_tex_file(expression, template_tex_file_body):
    result = os.path.join(
        TEX_DIR,
        tex_hash(expression, template_tex_file_body)
    ) + ".tex"
    if not os.path.exists(result):
        print("Writing \"%s\" to %s" % (
            "".join(expression), result
        ))
        new_body = template_tex_file_body.replace(
            TEX_TEXT_TO_REPLACE, expression
        )
        with open(result, "w", encoding = "utf-8") as outfile:
            outfile.write(new_body)
    return result

def tex_to_pdf(tex_file):
    result = tex_file.replace(".tex", ".pdf")
    if not os.path.exists(result):
        commands = [
            "xelatex",
            "-interaction=batchmode",
            "-halt-on-error",
            "-output-directory=" + TEX_DIR,
            tex_file,
            ">",
            os.devnull
        ]
        exit_code = os.system(" ".join(commands))
        if exit_code != 0:
            log_file = tex_file.replace(".tex", ".log")
            raise Exception(
                "XeLaTeX error converting to pdf. " +
                "See log output above or the log file: %s" % log_file)
    return result

def pdf_to_svg(pdf_file, regen_if_exists=False):
    result = pdf_file.replace(".pdf", ".svg")
    ## It's a bit counterintuitive, but...
    ## when converting a pdf file into an svg file,
    ## you need to use relative path, NOT absolute path!
    ## What is this!?
    current_dir = os.getcwd()
    pdf_file_path, pdf_file_name = os.path.split(pdf_file)
    result_path, result_name = os.path.split(result)
    os.chdir(pdf_file_path)
    if not os.path.exists(result):
        commands = [
            "dvisvgm",
            "-P",
            pdf_file_name,
            "-n",
            "-v",
            "0",
            "-o",
            result_name,
            ">",
            os.devnull
        ]
        os.system(" ".join(commands))
    os.chdir(current_dir)
    return result

