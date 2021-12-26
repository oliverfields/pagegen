# Changelog

<!--next-version-placeholder-->
Fixed: Executable content files where returning bytes instead of strings, this is python3 behaviour and has been fixed
Fixed: Page header preserve file name now is enforced, before the file name could have the default extension added, if specified in site.conf'
Feature: Added page header Exclude html minify, set to True to disable html minifying of the page
Fixed: Multiple variable in a line containing : where matching too much
Changed: Moved deploy_scripts to new deploy hook


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
