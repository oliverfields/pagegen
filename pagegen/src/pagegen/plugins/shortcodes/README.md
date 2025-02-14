# Shortcodes

Shortcodes are basically Python def's that can be embedded in page content or referenced from the site object, e.g. when generating templates. They are shorthand to make managing content easier.

In content they are as follows.

    <sc>figure('A bald eagle observes', 'Eagle', '/assets/images/eagle.jpg')</sc>

Or they can be used in Mako templates like so.

    <% f = objects['site'].shortcodes['figure'](site, page, 'A bald eagle observes', 'Eagle', '/assets/images/eagle.jpg') %>
    ${f}

The shortcode `figure` will generate the following HTML.

    <figure>
      <img src="/assets/images/eagle.jpg" alt="Eagle">
      <figcaption>A bald eagle observes</figcaption>
    </figure>

Which looks like this:

<sc>figure('A bald eagle observes', 'Eagle', '/assets/images/eagle-150x200.jpg')</sc>


## Creating new shortcodes

Shortcodes are Python functions(def) defined in `shortcodes.py`, in the site root directory. Shortcode functions must:

- Must accept one argument that is a dict containing relevant objects (mostly the site or page objects) and optinally more arguments e.g `def my_sc(objects, [, any other arguments])`
- Returns a string to embed in template/markdown content

The figure shortcode above could be written in `shortcodes.py` as follows.

    def figure(site, page, caption, alternative_text, src_path):
    
        html = '<figure>\n'
        html += '<img src="' + src_path + '" alt="' + alternative_text + '">\n'
        html += '<figcaption>' + caption + '</figcaption>\n'
        html += '</figure>\n'
    
        return html


## Built in shortcodes

Pagegen ships with ready to use built in shortcodes. Built in shortcodes will be overridden if a shortcode defined in `shortcodes.py` has the same name.

<sc>list_shortcodes()</sc>

In addition `pgn --init` will include `shortcodes.py_example` to illustrate further.
