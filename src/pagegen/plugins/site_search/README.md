# site_search

Creates index of site content at build time and provides a search template to search index using javascript on live site.

## Installation

Add the following configuration to `site.conf`.

    [site]
    ...
    enabled_plugins=[..., ]site_search

    [site_search]
    index_xpaths=//article

The [xpath](https://www.w3schools.com/xml/xpath_intro.asp) determines what parts of the HTML the plugin will index. Try to make this as specific as possible so that the index contains only the parts of the html dom that are unique to the page. It defaults to body, but that is most probably too braod.

To exclude many common words that you may not want indexed, copy [site_search_stopwords.txt](https://github.com/oliverfields/pagegen/blob/master/src/pagegen/plugins/site_search/site_search_stopwords.txt) to `content/site_search_stopwords.txt`.

Assuming you are using the [mako_templates plugin](https://github.com/oliverfields/pagegen/tree/master/src/pagegen/plugins/mako_templates) then copy the site_search plugin template [search.mako](https://github.com/oliverfields/pagegen/blob/master/src/pagegen/plugins/site_search/search.mako) to `themes/<theme name>/templates`.

Add a search form to your site, e.g. in the `base.mako` template.

    <form action="/search" method="GET">
      <input type="text" id="search-query" name="q">
      <input type="submit" id="search-submit" value="Search">
    </form>

Add search results page in `content directory`.

    title: Search
    template: search
    
    

For any pages that should not be indexed add page header `search: False`.

