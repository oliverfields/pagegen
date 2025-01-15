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
4. update template cache
5. template pass, for each file in cache that is older than its template add page to build list
6. add pages that are older than build dir to build list
7. build pages on build list
    7.1 run any plugin load functions
8. plugin prune cache
9. plugins run build functions


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

