import pytest
from git_web.helpers import content_preview
from git_web.helpers.known_mimetypes import register_extra_types


class TestGuessMimetype:
    @pytest.fixture(scope="class")
    def register_mimetypes(self):
        register_extra_types()

    def test_inbuilt(self):
        assert content_preview.guess_mimetype("test.txt") == "text/plain"

    @pytest.mark.usefixtures("register_mimetypes")
    def test_dot_file(self):
        assert content_preview.guess_mimetype(".gitignore") == "text/plain"

    @pytest.mark.usefixtures("register_mimetypes")
    def test_no_ext(self):
        assert content_preview.guess_mimetype("license") == "text/plain"
