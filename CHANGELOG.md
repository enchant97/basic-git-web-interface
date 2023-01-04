# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.8.0] - 2023-01-04
### Added
- Ability to move repositories into different directories
### Changed
- Update pip requirements
- Updated theme changer to V2
- Nicer powered by message
- Update docker image versions

## [1.7.0] - 2022-04-11
A look and feel update.
### Added
- Repository page last commit navigates to the commit
### Changed
- git commit log page improvements
- Improve repository tree breadcrumb
- Improve repository aside style
- Split pygments into separate file

## [1.6.0] - 2022-03-19
### Added
- Inbuilt 'Smart Git' HTTP access
- Add tests for new helper code
### Change
- Move directory listing into 'explore' page
- Always show homepage at index
- Update pip requirements
### Fixed
- Tags list shows a empty value when empty

## [1.5.0] - 2022-02-08
### Added
- Add message when there are no commits
- Redesign repository settings page
- Redesign branch select by adding tag selection and tree-ish
- Redesign commit log page
  - Add copy to clipboard functionality
  - Truncate commit hash & name
- Branch creation and deletion
- Allow for repository HEAD to be changed

### Changed
- Style improvements
- Updated pip requirements
- Use streamed responses for blob access
- Use new async version of git-interface
- Allow for tree-ish for commit log and tree navigation

### Fixed
- Implement fixed exception handling

## [1.4.0] - 2021-12-18
### Added
- Commit log count on repo view
- Relative link conversion for blobs
- Code highlighting with pygments
- Raw link when blob view not available
- Navigation breadcrumb for tree/blob navigation

### Changed
- Improved text blob rendering
- Better commit log navigation
- Split helper methods into separate files

### Fixed
- Style fixes for tree objects

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
