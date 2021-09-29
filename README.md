# Basic Git Web Server
This project (bgws) is designed to be basic. For example there is only one user account that has access to everything. It also doesn't have features like pull requests, issues, etc.

It has been designed to run through docker and it is recommended to run through a proxy like Nginx.

## Config
All configs are handled through environment variables.

| Name            | Description                 | Default     |
|:----------------|:----------------------------|:------------|
| REPOS_PATH      | Where the repos are stored  | /data/repos |
| REPOS_SSH_BASE  | SSH username and domain     |             |
| LOGIN_PASSWORD  | Password to login with      |             |
| SECRET_KEY      | Server secret key           |             |
| DISALLOWED_DIRS | any directory names to hide |             |
| DEFAULT_BRANCH  | the default branch name     | main        |
| WORKERS         | Number of Hypercorn workers | 1           |

> DISALLOWED_DIRS could be e.g. DISALLOWED_DIRS=".ssh,my-secrets"

## License
Copyright (C) 2021 Leo Spratt

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
