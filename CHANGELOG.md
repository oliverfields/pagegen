# Changelog

## 4.x.x

### Added

- Verbosity argument accepts level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- log_level setting in site section of site.conf
- Plugin site_search provides json index and javascript to implement a basic site search

### Fixes

- Create build dir if not exist
- live reload clears cache ensuring base_url etc are right

### Removed

- Excerpt plugin, suggest using headers instead
