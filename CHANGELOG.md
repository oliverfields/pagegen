# Changelog

<!--next-version-placeholder-->

## vx.x.x - yyyy-mm-dd

### Fixed

- Sitemaps now have corecct urls

## v3.3.3 - 2022-01-06

### Fixed

- Template page_file_name was incorrect for directories
- --serve disables deploy and post_deploy hooks for serving locally
- Removed superflous printing

### Added

- Page headers/frontmatter support custom headers. These can be referenced in templates using format {{page.<header name>}}. Example, if in a page the following header is set 'this is a custom header: At last', then in a template the following '{{page.this is a custom header}}' will be replaced with 'At last'
- Template variable/placeholder page_file_name added, contains what you expect
- Template variable/placeholder page_relative_url added, contains url relative to web root
- Template variable/placeholder default_extension added, contains default file extension


## v3.2.0 - 2021-12-30

### Added

- Added page header Exclude html minify, set to True to disable html minifying of the page
- New command argument -s|--serve <environment>, builds and serves the envionment on localhost, rebuilds if content is changed. Will force base_url to localhos:8000 when serving

### Changed

- Moved deploy_scripts functionality to new deploy hook
- Command line arguments changed. Environment must now be specified with -g or -s. --help argument added

### Fixed

- Executable content files where returning bytes instead of strings, this is python3 behaviour and has been fixed
- Page header preserve file name now is enforced, before the file name could have the default extension added, if specified in site.conf'
- Multiple variable in a line containing : where matching too much


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
