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
DRYRUNMSG = 'DRY RUN'

# Hooks
HOOK_PRE_BUILD = 'pgn_hook_pre_build'
HOOK_PRE_BUILD_LISTS = 'pgn_hook_pre_build_lists'
HOOK_POST_BUILD_LISTS = 'pgn_hook_post_build_lists'
HOOK_PAGE_DEPS = 'pgn_hook_page_deps'
HOOK_PAGE_PRE_BUILD = 'pgn_hook_page_pre_build'
HOOK_PAGE_RENDER_MARKUP = 'pgn_hook_page_render_markup'
HOOK_PAGE_RENDER_TEMPLATE = 'pgn_hook_page_render_template'
HOOK_PAGE_POST_BUILD = 'pgn_hook_page_post_build'
HOOK_POST_BUILD = 'pgn_hook_post_build'
