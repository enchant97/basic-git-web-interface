# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2021-12-10
### Added
- Multi-page commit log (WIP)
- Unit tests
- Sort repository tree
- Sort directory/repository list
- Implement safe path combiners
- Reserve certain directory/repository names
- Ability to view and modify ssh settings (public key and authorised keys)
- Basic tree navigation
- Blob/Raw file viewing (WIP)
- Repository list search-bar

### Changed
- Updated docker image to use Python 3.10
- Rename app to "Basic Git Web Interface"
- Use message flashing instead of http error codes
- Update pip requirements

### Fixed
- `create_ssh_uri` bug for when running on Windows systems
- Style fixes and improvements
- error when repos path does not exist

## [1.2.0] - 2021-12-05
### Added
- **Basic** markdown `README.md` rendering
- Implement a dark-mode scrollbar
- "last commit" message to repo tree view
- App Icon

### Changed
- Split app views into blueprints
- Move repo settings into separate page
- Improve site theme picker style
- Update pip requirements

## [1.1.1] - 2021-11-05
### Fixed
- docker health checking

## [1.1.0] - 2021-10-28
### Added
- add dark theme
- create compact docker image

## [1.0.0] - 2021-10-24
### Added
- initial release
