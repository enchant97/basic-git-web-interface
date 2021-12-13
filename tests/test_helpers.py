from pathlib import Path

import pytest
from git_interface.datatypes import TreeContent, TreeContentTypes
from git_web import helpers


@pytest.mark.usefixtures("app_config")
class TestHelpers:
    def test_is_allowed_dir(self, app_config: helpers.Config):
        assert helpers.is_allowed_dir(app_config.DISALLOWED_DIRS[0]) is False
        assert helpers.is_allowed_dir("/home/git/allowed-dir") is True

    def test_combine_full_dir(self, app_config: helpers.Config):
        repo_dir = "pytest-tests"
        expected = app_config.REPOS_PATH / repo_dir
        actual = helpers.combine_full_dir(repo_dir)
        assert expected == actual

    def test_combine_full_dir_repo(self, app_config: helpers.Config):
        repo_dir = "pytest-tests"
        repo_name = "combine-test"
        expected = app_config.REPOS_PATH / repo_dir / (repo_name + ".git")
        actual = helpers.combine_full_dir_repo(repo_dir, repo_name)
        assert expected == actual

    def test_sort_repo_tree(self):
        unsorted_content = (
            TreeContent("", TreeContentTypes.TREE, "", Path("my-folder"), ""),
            TreeContent("", TreeContentTypes.BLOB, "", Path("a-file.txt"), ""),
            TreeContent("", TreeContentTypes.BLOB, "", Path("something"), ""),
            TreeContent("", TreeContentTypes.TREE, "", Path("hi-secrets"), ""),
            TreeContent("", TreeContentTypes.BLOB, "", Path("hello.py"), ""),
            TreeContent("", TreeContentTypes.TREE, "", Path("hello"), ""),
        )
        expected_order = (
            TreeContent("", TreeContentTypes.TREE, "", Path("hello"), ""),
            TreeContent("", TreeContentTypes.TREE, "", Path("hi-secrets"), ""),
            TreeContent("", TreeContentTypes.TREE, "", Path("my-folder"), ""),
            TreeContent("", TreeContentTypes.BLOB, "", Path("a-file.txt"), ""),
            TreeContent("", TreeContentTypes.BLOB, "", Path("hello.py"), ""),
            TreeContent("", TreeContentTypes.BLOB, "", Path("something"), ""),
        )

        actual_order = helpers.sort_repo_tree(unsorted_content)

        assert len(actual_order) == len(expected_order)
        assert expected_order == actual_order

    def test_create_ssh_uri(self, app_config: helpers.Config):
        repo_name = "pytest-ssh-uri-test.git"
        repo_dir = "pytest-tests"
        full_path = app_config.REPOS_PATH / repo_dir / repo_name
        expected = app_config.REPOS_SSH_BASE + f":{repo_dir}/{repo_name}"
        actual = helpers.create_ssh_uri(full_path)
        assert expected == actual

    def test_is_valid_clone_url(self):
        assert helpers.is_valid_clone_url("https://gitweb.lan/my-dir/my-repo.git") is True
        assert helpers.is_valid_clone_url("http://gitweb.lan/my-dir/a-repo.git") is True
        assert helpers.is_valid_clone_url("http://gitweb.lan/a-repo.git") is True
        assert helpers.is_valid_clone_url("ftp://gitweb.lan/my-dir/my-repo.git") is False
        assert helpers.is_valid_clone_url("://gitweb.lan/my-dir/my-repo.git") is False
        assert helpers.is_valid_clone_url("//my-dir/my-repo.git") is False
        assert helpers.is_valid_clone_url("") is False
        assert helpers.is_valid_clone_url("../my-repo/my-repo.git") is False

    def test_is_commit_hash(self):
        assert helpers.is_commit_hash("44Afff") is True
        assert helpers.is_commit_hash("42481a7") is True
        assert helpers.is_commit_hash("&& rm -rf .") is False
        assert helpers.is_commit_hash("42481a7@") is False
        assert helpers.is_commit_hash("") is False

    def test_is_valid_repo_name(self):
        assert helpers.is_valid_repo_name("my-repo") is True
        assert helpers.is_valid_repo_name("valid") is True
        assert helpers.is_valid_repo_name("valid_underscore") is True
        assert helpers.is_valid_repo_name("valid-1234") is True
        assert helpers.is_valid_repo_name("a"*100) is True
        assert helpers.is_valid_repo_name("a"*20) is True
        assert helpers.is_valid_repo_name("with a space") is False
        assert helpers.is_valid_repo_name("symbols-$$.") is False
        assert helpers.is_valid_repo_name("") is False
        assert helpers.is_valid_repo_name("()") is False
        assert helpers.is_valid_repo_name("../breakout/repo-name") is False
        assert helpers.is_valid_repo_name("a"*200) is False

    def test_is_valid_directory_name(self):
        assert helpers.is_valid_directory_name("my-directory") is True
        assert helpers.is_valid_directory_name("valid") is True
        assert helpers.is_valid_directory_name("valid_underscore") is True
        assert helpers.is_valid_directory_name("valid-1234") is True
        assert helpers.is_valid_repo_name("a"*100) is True
        assert helpers.is_valid_repo_name("a"*20) is True
        assert helpers.is_valid_directory_name("with a space") is False
        assert helpers.is_valid_directory_name("symbols-$$.") is False
        assert helpers.is_valid_directory_name("") is False
        assert helpers.is_valid_directory_name("()") is False
        assert helpers.is_valid_directory_name("../breakout/directory-name") is False
        assert helpers.is_valid_repo_name("a"*200) is False

    def test_safe_combine_full_dir(self, app_config: helpers.Config):
        repo_dir = "pytest-tests"
        expected = app_config.REPOS_PATH / repo_dir
        actual = helpers.safe_combine_full_dir(repo_dir)
        assert expected == actual

    def test_safe_combine_full_dir_invalid(self):
        with pytest.raises(ValueError):
            helpers.safe_combine_full_dir("not safe!@:;")

    def test_safe_combine_full_dir_repo(self, app_config: helpers.Config):
        repo_dir = "pytest-tests"
        repo_name = "combine-test"
        expected = app_config.REPOS_PATH / repo_dir / (repo_name + ".git")
        actual = helpers.safe_combine_full_dir_repo(repo_dir, repo_name)
        assert expected == actual

    def test_safe_combine_full_dir_repo_invalid(self):
        with pytest.raises(ValueError):
            helpers.safe_combine_full_dir_repo("not safe!@:;", "safe")
        with pytest.raises(ValueError):
            helpers.safe_combine_full_dir_repo("safe", "not safe!@:*(33;")

    def test_is_name_reserved(self):
        assert helpers.is_name_reserved("login") is True
        assert helpers.is_name_reserved("logout") is True
        assert helpers.is_name_reserved("random") is False

    def test_does_path_contain(self):
        paths = (
            Path("test/hello"),
            Path("a/something"),
            Path("test/hello this is a test"),
            Path("something/my filename"),
            Path("test/this is amazing hello"),
        )
        result = tuple(filter(lambda path: helpers.does_path_contain(path, "hello"), paths))
        assert len(result) == 3

    def test_path_to_tree_components(self):
        path = Path("a/b/c/test.txt")

        excepted_output = (
            helpers.PathComponent(Path("a"), "a", False),
            helpers.PathComponent(Path("a/b"), "b", False),
            helpers.PathComponent(Path("a/b/c"), "c", False),
            helpers.PathComponent(Path("a/b/c/test.txt"), "test.txt", True),
        )
        actual_output = tuple(helpers.path_to_tree_components(path))

        assert excepted_output == actual_output
