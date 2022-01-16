# Changelog

<!--next-version-placeholder-->
## vX.X.X - yyyy-mm-dd

### Added

- When using --serve any changes to the site will trigger rebuild. Pages being served will reload if a rebuild has occured. The F5 key will appreciate
- Markdown support, in site.conf set default "markup=md" to use markdown as default, can be overriden in page headers using "Markdown: mk". Default is rst
-


### Fixed

- Pages with header exclude link chain where not being converted to html


### Removed

- Header_profiles functionality


## v3.4.0 - 2022-01-13

### Added

- Mako template engine, now templates can have full power of Mako, incl if else, loops and full on python code execution
- Page headers/frontmatter support custom headers. These can be referenced in templates using format {{page.<header name>}}. Example, if in a page the following header is set 'this is a custom header: At last', then in a template the following '{{page.this is a custom header}}' will be replaced with 'At last'
- Template variable/placeholder page_file_name added, contains what you expect
- Template variable/placeholder page_relative_url added, contains url relative to web root
- Template variable/placeholder default_extension added, contains default file extension

### Fixed

- Template page_file_name was incorrect for directories
- --serve disables deploy and post_deploy hooks for serving locally
- Removed superflous printing
- Sitemaps now have corecct urls
- Hooks now only execute if they have execute rights (linux)


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
