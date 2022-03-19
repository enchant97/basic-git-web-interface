# Basic Git Web Interface
This project (bgwi) is designed to be basic. For example there is only one user account that has access to everything. It also doesn't have features like pull requests, issues, etc.

It has been designed to run through docker and it is recommended to run through a proxy like Nginx.

## Features
- Password protection for web-ui
- No separate accounts
- Create/Delete Repo Folders
- Manage Repos
    - Create
    - Delete
    - Rename
    - List Commits
    - View Branches
    - Run Git Maintenance
    - Import Repos from http/s sources (with no authentication)
    - Download archives of repos
    - View tree of repo
    - SSH url generation
- Inbuilt 'Smart Git' Http access
- Icon based interface
- Basic theme that is "easy on the eyes"
- Inbuilt health check url
- Minimal docker image (uses alpine)

## About The Repo
- This repo uses 'main' as the develop branch and should be treating unstable or unfinished. If you want a stable release please use the tags/releases.
- The [CHANGELOG](CHANGELOG.md) contains a history of changes that happened with each release.

## Config
All configs are handled through environment variables.

| Name                 | Description                               | Default     |
|:---------------------|:------------------------------------------|:------------|
| REPOS_PATH           | Where the repos are stored                | /data/repos |
| REPOS_SSH_BASE       | SSH username and domain                   |             |
| REPOS_HTTP_BASE      | The url for accessing for using git http  |             |
| LOGIN_PASSWORD       | Password to login with                    |             |
| SECRET_KEY           | Server secret key                         |             |
| DISALLOWED_DIRS      | Any directory names to hide               | -           |
| DEFAULT_BRANCH       | The default branch name                   | main        |
| MAX_COMMIT_LOG_COUNT | Max number of commits to show             | 20          |
| SSH_PUB_KEY_PATH     | Path to public ssh key                    | -           |
| SSH_AUTH_KEYS_PATH   | Path to authorised ssh keys               | -           |
| HTTP_GIT_ENABLED     | Whether to allow git http requests        | 1           |
| WORKERS              | Number of Hypercorn workers               | 1           |

> Default values indicated with '-' are not required

> REPOS_SSH_BASE should look like this: `git@mydomain.lan`

> REPOS_HTTP_BASE should look like this: `https://git.mydomain.lan`

> DISALLOWED_DIRS must be a JSON array be e.g. DISALLOWED_DIRS=[".ssh", "my-secrets"]

## Git HTTP Access
To access it you need a git client that supports the smart protocol, dumb is **not** supported. To login, use 'admin' as username and the 'LOGIN_PASSWORD' value as the password. If you do not want the inbuilt Git HTTP access you can turn it off in the config.

## License
The licenses for this project can be found in the `LICENSE` file.
