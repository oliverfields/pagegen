# Changelog

<!--next-version-placeholder-->
Bug fix: Executable content files where returning bytes instead of strings, this is python3 behaviour and has been fixed

## v3.1.1 - 2021-12-14

### Changed

- pagegen --init now includes examples of scripts


## v3.1.0 - 2021-12-13

### Added

- Custom deploy scripts per environment, currently ftp is supported
- Minify html, css and javascript options

### Changed

- Refactored variable initializing, under the hood..

### Removed

- Upload to FTP functionality. New deploy_scripts/ftp.py are drop in replacement
