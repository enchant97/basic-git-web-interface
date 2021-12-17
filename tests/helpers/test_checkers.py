from pathlib import Path

from git_web.helpers import checkers
from git_web.helpers.config import Config


class TestCheckers:
    def test_is_allowed_dir(self, app_config: Config):
        assert checkers.is_allowed_dir(app_config.DISALLOWED_DIRS[0]) is False
        assert checkers.is_allowed_dir("/home/git/allowed-dir") is True

    def test_is_valid_clone_url(self):
        assert checkers.is_valid_clone_url("https://gitweb.lan/my-dir/my-repo.git") is True
        assert checkers.is_valid_clone_url("http://gitweb.lan/my-dir/a-repo.git") is True
        assert checkers.is_valid_clone_url("http://gitweb.lan/a-repo.git") is True
        assert checkers.is_valid_clone_url("ftp://gitweb.lan/my-dir/my-repo.git") is False
        assert checkers.is_valid_clone_url("://gitweb.lan/my-dir/my-repo.git") is False
        assert checkers.is_valid_clone_url("//my-dir/my-repo.git") is False
        assert checkers.is_valid_clone_url("") is False
        assert checkers.is_valid_clone_url("../my-repo/my-repo.git") is False

    def test_is_commit_hash(self):
        assert checkers.is_commit_hash("44Afff") is True
        assert checkers.is_commit_hash("42481a7") is True
        assert checkers.is_commit_hash("&& rm -rf .") is False
        assert checkers.is_commit_hash("42481a7@") is False
        assert checkers.is_commit_hash("") is False

    def test_is_valid_repo_name(self):
        assert checkers.is_valid_repo_name("my-repo") is True
        assert checkers.is_valid_repo_name("valid") is True
        assert checkers.is_valid_repo_name("valid_underscore") is True
        assert checkers.is_valid_repo_name("valid-1234") is True
        assert checkers.is_valid_repo_name("a"*100) is True
        assert checkers.is_valid_repo_name("a"*20) is True
        assert checkers.is_valid_repo_name("with a space") is False
        assert checkers.is_valid_repo_name("symbols-$$.") is False
        assert checkers.is_valid_repo_name("") is False
        assert checkers.is_valid_repo_name("()") is False
        assert checkers.is_valid_repo_name("../breakout/repo-name") is False
        assert checkers.is_valid_repo_name("a"*200) is False

    def test_is_valid_directory_name(self):
        assert checkers.is_valid_directory_name("my-directory") is True
        assert checkers.is_valid_directory_name("valid") is True
        assert checkers.is_valid_directory_name("valid_underscore") is True
        assert checkers.is_valid_directory_name("valid-1234") is True
        assert checkers.is_valid_repo_name("a"*100) is True
        assert checkers.is_valid_repo_name("a"*20) is True
        assert checkers.is_valid_directory_name("with a space") is False
        assert checkers.is_valid_directory_name("symbols-$$.") is False
        assert checkers.is_valid_directory_name("") is False
        assert checkers.is_valid_directory_name("()") is False
        assert checkers.is_valid_directory_name("../breakout/directory-name") is False
        assert checkers.is_valid_repo_name("a"*200) is False

    def test_is_name_reserved(self):
        assert checkers.is_name_reserved("login") is True
        assert checkers.is_name_reserved("logout") is True
        assert checkers.is_name_reserved("random") is False

    def test_does_path_contain(self):
        paths = (
            Path("test/hello"),
            Path("a/something"),
            Path("test/hello this is a test"),
            Path("something/my filename"),
            Path("test/this is amazing hello"),
        )
        result = tuple(filter(lambda path: checkers.does_path_contain(path, "hello"), paths))
        assert len(result) == 3
