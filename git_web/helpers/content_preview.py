from markdown_it import MarkdownIt
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import (find_lexer_class_by_name,
                             find_lexer_class_for_filename)


def markdown_it_highlighter(content, langName, langAttrs):
    if not langName:
        langName = "text"
    lexer = find_lexer_class_by_name(langName)()
    return highlight(content, lexer, HtmlFormatter(nowrap=True))


def highlight_by_ext(content: str, ext: str) -> str:
    lexer = find_lexer_class_for_filename(ext)()
    return highlight(content, lexer, HtmlFormatter(nowrap=True))


def render_markdown(content: str) -> str:
    md = MarkdownIt("gfm-like", {"html": False, "highlight": markdown_it_highlighter})
    return md.render(content)
