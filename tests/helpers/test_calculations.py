from pathlib import Path

import pytest
from git_interface.datatypes import TreeContent, TreeContentTypes
from git_web.helpers import calculations as calc
from git_web.helpers.config import Config
from git_web.helpers.types import PathComponent


@pytest.mark.usefixtures("app_config")
class TestCalculations:
    def test_combine_full_dir(self, app_config: Config):
        repo_dir = "pytest-tests"
        expected = app_config.REPOS_PATH / repo_dir
        actual = calc.combine_full_dir(repo_dir)
        assert expected == actual

    def test_combine_full_dir_repo(self, app_config: Config):
        repo_dir = "pytest-tests"
        repo_name = "combine-test"
        expected = app_config.REPOS_PATH / repo_dir / (repo_name + ".git")
        actual = calc.combine_full_dir_repo(repo_dir, repo_name)
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

        actual_order = calc.sort_repo_tree(unsorted_content)

        assert len(actual_order) == len(expected_order)
        assert expected_order == actual_order

    def test_create_ssh_uri(self, app_config: Config):
        repo_name = "pytest-ssh-uri-test.git"
        repo_dir = "pytest-tests"
        full_path = app_config.REPOS_PATH / repo_dir / repo_name
        expected = app_config.REPOS_SSH_BASE + f":{repo_dir}/{repo_name}"
        actual = calc.create_ssh_uri(full_path)
        assert expected == actual

    def test_safe_combine_full_dir(self, app_config: Config):
        repo_dir = "pytest-tests"
        expected = app_config.REPOS_PATH / repo_dir
        actual = calc.safe_combine_full_dir(repo_dir)
        assert expected == actual

    def test_safe_combine_full_dir_invalid(self):
        with pytest.raises(ValueError):
            calc.safe_combine_full_dir("not safe!@:;")

    def test_safe_combine_full_dir_repo(self, app_config: Config):
        repo_dir = "pytest-tests"
        repo_name = "combine-test"
        expected = app_config.REPOS_PATH / repo_dir / (repo_name + ".git")
        actual = calc.safe_combine_full_dir_repo(repo_dir, repo_name)
        assert expected == actual

    def test_safe_combine_full_dir_repo_invalid(self):
        with pytest.raises(ValueError):
            calc.safe_combine_full_dir_repo("not safe!@:;", "safe")
        with pytest.raises(ValueError):
            calc.safe_combine_full_dir_repo("safe", "not safe!@:*(33;")

    def test_path_to_tree_components(self):
        path = Path("a/b/c/test.txt")

        excepted_output = (
            PathComponent(Path("a"), "a", False),
            PathComponent(Path("a/b"), "b", False),
            PathComponent(Path("a/b/c"), "c", False),
            PathComponent(Path("a/b/c/test.txt"), "test.txt", True),
        )
        actual_output = tuple(calc.path_to_tree_components(path))

        assert excepted_output == actual_output
