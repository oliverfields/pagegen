├── .cache
       template
       page
       plugins
           tags
           search
           sitemap
├── content
│   ├── 404
│   ├── about
│   ├── archive
│   ├── assets
│   ├── feed.rss
│   ├── .htaccess
│   ├── index
│   ├── practical-mysticisim-series
│   ├── practical-mysticisim-summary
│   ├── robots.txt
│   ├── search
│   ├── search-index.json
│   ├── sitemap.txt
│   ├── sitemap.xml
│   └── tag
│       ├── evelyn-underhill
│       ├── mysticisim
│       └── spirituality
├── plugins
│   ├── list-todos
│   ├── rss
│   │   └── plugin.conf
│   ├── search
│   │   └── stopwords.txt
│   ├── sitemap
│   └── tags
├── build
├── site.env
└── themes
    └── ebbandflow
        ├── assets
        │   ├── favicon.ico
        │   ├── site.css
        │   └── site.js
        └── templates
            ├── base.mako
            ├── home_page.mako
            ├── pages.mako
            ├── search.mako
            ├── tag.mako
            └── tags.mako

1. plugins register paths -> update content dir
2. make content list
3. prune build dir

x. load dependency graph
y. check build list items against dependency graph and add any items to build list

4. update template cache
5. template pass, for each file in cache that is older than its template add page to build list
6. add pages that are older than build dir to build list
7. build pages on build list
    7.1 run any plugin load functions
8. plugin prune cache
9. plugins run build functions




dependency graph
{
  '<content_path>': [
    '<build_path>', # Build path dependency
    ...
  ]
}

when item is found that needs building because of dependency graph, also check it's dependencies


Plugin architecture
init -> e.g. add files to content dir
prune_cache -> after page loads prune the caches if required
page_load -> when a page loads plugin gets a peak and can do stuff here, e.g. write caches
build -> plugin does what it has to do
shortcodes -> make scs available in markdown

sitemap
  register -> sitemap.txt and sitemap.xml
  page_load -> add url to sitemap cache file if not header sitemap exclude: True
  prune -> if page deleted then remove it from cache file
  build -> update sitemap.* if it is older than any of the files
  custom markdown generation

plugin candidates
archive
tags
search
pagination
prev/next links
backlinks
rss feed

plugin_add_hook(pre_build, sequence=10)
if a plugin adds itself and there already exists a hook registered with same sequence integer then raise error. point of this is to make explicit the sequence that hooks are executed in, e.g. the markdown plugin must have a sequence lower than the template plugin so that the page content is first converted to  markdown, and then the template is applied creating the final html

Template plugin:

    PLUGIN pre_build: before the fun starts

        plugin loads its own dep graph showing what templates depend on each other. if template has changed since it deps where calculated, then write new cache

    PLUGIN pre_build_lists
    PLUGIN post_build_lists
    PLUGIN page_dep_check: Chance for plugin to check if any pages need to be rebuilt, the plugin probably maintains its own cache for this purpose

        check page template for any dependencies against the dependencies that the template plugin maintains as pages are built, see the post_page_build hook

    PLUGIN pre_page_build: before page is generated plugin can inspect and do stuff
    PLUGIN add_template_functions

    PLUGIN page_generate, if exists then use plugin function instead of builtin one, make it easy to use something other than markdown, builtin just copies page content verbatim

        template plugin adds a step in the pipline for generating the page, another normal pipleline step is the markdown to html generator, the rusult of the pipeline is written to build target

    PLUGIN post_page_build: after page is generated plugin can inspect page and do stuff, e.g update any caches or such

        plugin figures out what template files the page relays on based on the page header template value. adding this dependency to the site dep_graph cache

    PLUGIN post_build: afterparty

