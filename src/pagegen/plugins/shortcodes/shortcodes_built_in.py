def built_in_quote(site, page, quote, by=False):
    """ Add a quote markup """

    html = '<div class="quote"><q class="quote-text">' + quote + '</q>'

    if by:
        html += '<div class="quote-by">— ' + by + '</div>'

    html += '</div>'

    return html


