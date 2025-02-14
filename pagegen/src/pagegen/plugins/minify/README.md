# Minify HTML, CSS and JavaScript

Page HTML and/or .css and .js files in assets directories.


## Page HTML

Minify HTML of a page during rendering. Page header `Minify HTML: False` will disable minification for the given page.


## CSS and Javascript

All .css and .js files in `assets` or `themes/<theme name>/assets` directories get minified in `build` directory.

CSS and JavaScript minification can be disabled from `site.conf` by setting section `[minify]` setting `minify_css` or `minify_js` to `False`.
