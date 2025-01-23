ESCAPECODES = {
  "red": "\033[1;31m",
  "yellow": "\033[1;33m",
  "green": "\033[1;32m",
  "blue": "\033[1;34m",
  "default": "\033[0m"
}

SITE_CONF = 'site.conf'
CONTENT_DIR = 'content'
BUILD_DIR = 'build'
ASSET_DIR = 'assets'
CACHE_DIR = '.cache'
THEME_DIR = 'themes'
THEME_TEMPLATE_DIR = 'templates'
PLUGIN_DIR = 'plugins'
LOCK_FILE = '.pgn_lock'

# Hooks
HOOK_PRE_BUILD = 'pre_build'
HOOK_PRE_BUILD_LISTS = 'pre_build_lists'
HOOK_POST_BUILD_LISTS = 'post_build_lists'
HOOK_PAGE_DEPS = 'page_deps'
HOOK_PAGE_PRE_BUILD = 'page_pre_build'
HOOK_PAGE_RENDER_MARKUP = 'page_render_markup'
HOOK_PAGE_RENDER_TEMPLATE = 'page_render_template'
HOOK_PAGE_POST_BUILD = 'page_post_build'
HOOK_POST_BUILD = 'post_build'
