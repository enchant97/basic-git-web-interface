import mimetypes
from urllib.parse import urlparse

from markdown_it import MarkdownIt
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, get_lexer_for_filename
from pygments.util import ClassNotFound


def markdown_it_highlighter(content, langName, langAttrs):
    """
    Code highlighter for markdown-it using pygments
    """
    if not langName:
        langName = "text"
    try:
        lexer = get_lexer_by_name(langName)
    except ClassNotFound:
        lexer = get_lexer_by_name("text")
    finally:
        return highlight(content, lexer, HtmlFormatter(nowrap=True))


def markdown_it_render_readme_link(self, tokens, idx, options, env):
    """
    Markdown-it render rule for a readme
    link to convert relative links to absolute
    """
    token = tokens[idx]
    if not urlparse(token.attrs["href"]).netloc:
        tokens[idx].attrSet("href", options["url_relative_to_blob"] + token.attrs["href"])
    return self.renderToken(tokens, idx, options, env)


def markdown_it_render_readme_image(self, tokens, idx, options, env):
    """
    Markdown-it render rule for a readme
    image to convert relative links to absolute
    """
    token = tokens[idx]
    if not urlparse(token.attrs["src"]).netloc:
        tokens[idx].attrSet("src", options["url_relative_to_raw"] + token.attrs["src"])
    return self.renderToken(tokens, idx, options, env)


def highlight_by_ext(content: str, ext: str) -> str:
    """
    Highlight some text based on an extention

        :param content: The file content
        :param ext: The file extention
        :return: Rendered HTML
    """
    try:
        lexer = get_lexer_for_filename(ext)
    except ClassNotFound:
        lexer = get_lexer_by_name("text")
    finally:
        return highlight(content, lexer, HtmlFormatter(nowrap=True))


def render_markdown(
        content: str,
        url_relative_to_blob: str = None,
        url_relative_to_raw: str = None) -> str:
    """
    Render a markdown string into HTML using markdown-it

        :param content: Markdown content
        :param url_relative_to_blob: Url to use for converting
                                     relative paths, defaults to None
        :param url_relative_to_raw: Url to use for converting
                                    relative paths, defaults to None
        :return: Rendered HTML
    """
    md = MarkdownIt(
        "gfm-like",
        {
            "html": False,
            "highlight": markdown_it_highlighter,
            "url_relative_to_blob": url_relative_to_blob,
            "url_relative_to_raw": url_relative_to_raw,
        }
    )
    if url_relative_to_blob:
        md.add_render_rule("link_open", markdown_it_render_readme_link)
    if url_relative_to_raw:
        md.add_render_rule("image", markdown_it_render_readme_image)
    return md.render(content)


def guess_mimetype(file_path: str) -> str | None:
    """
    Guess a mimetype

        :param file_path: The filepath to use for a guess
        :return: The guessed mimetype
    """
    # TODO add content guessing for fallback
    guess_path = None
    if file_path.startswith("."):
        guess_path = "file" + file_path
    elif "." in file_path:
        guess_path = file_path
    else:
        guess_path = "file." + file_path
    return mimetypes.guess_type(guess_path)[0]
