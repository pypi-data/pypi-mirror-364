# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## 1.1.0
### Fixed
- Fix separator in categories parsing in the python version to use coma
### Changed
- Update python classifiers
- Use parallel matrix in CI
### Added
- can create git branch
### Removed
- upx removed, it may cause problem and other rust binaries usualy don’t use it
- yapf removal as it seems not maintained anymore

## 1.0.2
### Fixed
- Fix category name Remove to Removed
### Added
- Add Arch PKGBUILDs for rust and python

## 1.0.1
### Fixed
- Fix extra newlines in python version
### Changed
- Fix newlines in own changelog + typo in readme

## 1.0.0
### Security
- Security updates

### Fixed
- Fix dry-run for merge in python

### Changed
- New list format (#1)
- Sync Python and Rust command line format (#2)
- Allow same relative output for list -p for python <3.12
- Allow to find root by finding .editorconfig in python as in rust

### Added
- Add git integration and --no-git config parameter (#3)
- Allow to commit using part changelog files (#4)
- Allow the rust version to also read pyproject.toml file


## 0.1.0
### Added
- Complete CI/CD for rust and python
- Publishing to Pypi
- Merge the rust version into the python version.
