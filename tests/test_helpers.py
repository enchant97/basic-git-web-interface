from pathlib import Path

import pytest
from git_interface.datatypes import TreeContent, TreeContentTypes
from git_web import helpers


@pytest.fixture()
def app_config() -> helpers.Config:
    return helpers.get_config()


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
