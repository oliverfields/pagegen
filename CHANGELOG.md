# Changelog

## 4.x.x

### Added

- Verbosity argument accepts level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- log_level setting in site section of site.conf
- Plugin site_search provides json index and javascript to implement a basic site search
- Serve build dir locally managing base_url without changes to build dir. Replaces live reload

### Fixes

- Create build dir if not exist

### Removed

- Excerpt plugin, suggest using headers instead
- live reload
