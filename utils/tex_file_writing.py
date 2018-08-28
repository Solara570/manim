
import os
import hashlib

from constants import TEX_DIR
from constants import TEX_TEXT_TO_REPLACE


def tex_hash(expression, template_tex_file_body):
    id_str = str(expression + template_tex_file_body)
    hasher = hashlib.sha256()
    hasher.update(id_str.encode())
    # Truncating at 16 bytes for cleanliness
    return hasher.hexdigest()[:16]


def enc_conv(filename, in_enc, out_enc):
    content = open(filename, "r").read()
    conv_content = content.decode(in_enc).encode(out_enc)
    open(filename, "w").write(conv_content)


def tex_to_svg_file(expression, template_tex_file_body, encoding):
    tex_file = generate_tex_file(expression, template_tex_file_body, encoding)
    dvi_file = tex_to_dvi(tex_file)
    return dvi_to_svg(dvi_file)


def generate_tex_file(expression, template_tex_file_body, encoding):
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
        with open(result, "w") as outfile:
            outfile.write(new_body)
    if encoding != "UTF8":
        try:
            enc_conv(result, in_enc = "UTF8", out_enc = encoding)
        except:
            pass
    return result


def get_null():
    if os.name == "nt":
        return "NUL"
    return "/dev/null"


def tex_to_dvi(tex_file):
    result = tex_file.replace(".tex", ".dvi")
    if not os.path.exists(result):
        commands = [
            "latex",
            "-interaction=batchmode",
            "-halt-on-error",
            "-output-directory=" + TEX_DIR,
            tex_file,
            ">",
            get_null()
        ]
        exit_code = os.system(" ".join(commands))
        if exit_code != 0:
            log_file = tex_file.replace(".tex", ".log")
            raise Exception(
                "Latex error converting to dvi. "
                "See log output above or the log file: %s" % log_file)
    return result


def dvi_to_svg(dvi_file, regen_if_exists=False):
    """
    Converts a dvi, which potentially has multiple slides, into a
    directory full of enumerated pngs corresponding with these slides.
    Returns a list of PIL Image objects for these images sorted as they
    where in the dvi
    """
    result = dvi_file.replace(".dvi", ".svg")
    if not os.path.exists(result):
        commands = [
            "dvisvgm",
            dvi_file,
            "-n",
            "-v",
            "0",
            "-o",
            result,
            ">",
            get_null()
        ]
        os.system(" ".join(commands))
    return result
