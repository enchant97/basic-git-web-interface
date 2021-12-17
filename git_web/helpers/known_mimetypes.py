from mimetypes import add_type

TYPES = (
    ("text/plain", ".yml"),
    ("text/markdown", ".md"),
    ("text/plain", ".gitignore"),
    ("text/plain", ".license"),
    ("text/plain", ".dockerfile"),
    ("text/plain", ".dockerignore"),
)


def register_extra_types():
    for type_ in TYPES:
        add_type(*type_)
