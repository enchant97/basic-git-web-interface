from mimetypes import guess_type

from git_web.helpers.known_mimetypes import register_extra_types


def test_register_extra_types():
    register_extra_types()
    assert guess_type("file.md")[0] == "text/markdown"
