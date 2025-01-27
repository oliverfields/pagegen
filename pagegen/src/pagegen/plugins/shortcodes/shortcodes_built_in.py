def built_in_list_posts(site, page, posts_dir, max_posts_limit):
    """List posts found in posts_dir"""

    html = ''
    posts = []
    counter = 0

    if not isinstance(max_posts_limit, int):
        max_posts_limit = int(max_posts_limit)

    # Strip leading / if present
    if posts_dir.startswith('/'):
        posts_dir = posts_dir[1:]

    for p in site.page_list:
        if p.source_path.startswith(site.content_dir + '/' + posts_dir):
            posts.append(p)

    if len(posts) == 0:
        return 'No posts yet..'

    sorted_posts = sorted(posts, key=lambda d: d.headers['publish'], reverse=True)

    for p in sorted_posts:
        counter += 1

        if counter == max_posts_limit:
            break

        if p.excerpt:
            excerpt = '<br />' + p.excerpt
        else:
            excerpt = ''

        html += '<li>' + p.headers['publish'] + ' <a href="' + p.url_path + '">' + p.title + '</a>' + excerpt + '</li>'

    return '<ol>' + html + '</ol>'


def built_in_quote(site, page, quote, by=False):
    """ Add a quote markup """

    html = '<div class="quote"><q class="quote-text">' + quote + '</q>'

    if by:
        html += '<div class="quote-by">— ' + by + '</div>'

    html += '</div>'

    return html


