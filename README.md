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
- Icon based interface
- Basic theme that is "easy on the eyes"
- Inbuilt health check url
- Minimal docker image (uses alpine)

## About The Repo
- This repo uses 'main' as the develop branch and should be treating unstable or unfinished. If you want a stable release please use the tags/releases.
- The [CHANGELOG](CHANGELOG.md) contains a history of changes that happened with each release.

## Config
All configs are handled through environment variables.

| Name               | Description                 | Default     |
|:-------------------|:----------------------------|:------------|
| REPOS_PATH         | Where the repos are stored  | /data/repos |
| REPOS_SSH_BASE     | SSH username and domain     |             |
| LOGIN_PASSWORD     | Password to login with      |             |
| SECRET_KEY         | Server secret key           |             |
| DISALLOWED_DIRS    | any directory names to hide | -           |
| DEFAULT_BRANCH     | the default branch name     | main        |
| SSH_PUB_KEY_PATH   | path to public ssh key      | -           |
| SSH_AUTH_KEYS_PATH | path to authorised ssh keys | -           |
| WORKERS            | Number of Hypercorn workers | 1           |

> DISALLOWED_DIRS could be e.g. DISALLOWED_DIRS=".ssh,my-secrets"

## License
The licenses for this project can be found in the `LICENSE` file.
