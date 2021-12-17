import mimetypes

from markdown_it import MarkdownIt
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, get_lexer_for_filename
from pygments.util import ClassNotFound


def markdown_it_highlighter(content, langName, langAttrs):
    if not langName:
        langName = "text"
    try:
        lexer = get_lexer_by_name(langName)
    except ClassNotFound:
        lexer = get_lexer_by_name("text")
    finally:
        return highlight(content, lexer, HtmlFormatter(nowrap=True))


def highlight_by_ext(content: str, ext: str) -> str:
    try:
        lexer = get_lexer_for_filename(ext)
    except ClassNotFound:
        lexer = get_lexer_by_name("text")
    finally:
        return highlight(content, lexer, HtmlFormatter(nowrap=True))


def render_markdown(content: str) -> str:
    md = MarkdownIt("gfm-like", {"html": False, "highlight": markdown_it_highlighter})
    return md.render(content)


def guess_mimetype(file_path: str) -> str | None:
    # TODO add content guessing for fallback
    guess_path = None
    if file_path.startswith("."):
        guess_path = "file" + file_path
    elif "." in file_path:
        guess_path = file_path
    else:
        guess_path = "file." + file_path
    return mimetypes.guess_type(guess_path)[0]
