<%page args = "site, posts_dir, max_posts_limit" />
<%
  blog_posts_html = ''
  posts = []
  counter = 0
  # Just makes the argument limit more intuitive
  max_posts_limit = max_posts_limit + 1

  sorted_pages = sorted(site.page_list, key=lambda d: d.source_path, reverse=True)
  # Strip leading / if present
  if posts_dir.startswith('/'):
    posts_dir = posts_dir[1:]

  # Make list of all posts identified by template
  for p in sorted_pages:
    if p.headers['template'] == 'pages.mako' and p.headers['publish']:
      posts.append(p)

  if len(posts) == 0:
    return 'No posts yet..'

  sorted_posts = sorted(posts, key=lambda x: x.headers['publish'], reverse=True)

  # Create html for posts
  for p in sorted_posts:
    counter += 1

    if counter == max_posts_limit:
      break
    else:
      # On homepage need to know what is the link to the next (first "off-page") blog post
      site.homepage_previous_post = p

    if p.excerpt:
      excerpt = '<div class="post-excerpt">' + p.excerpt + '</div>'
    else:
      excerpt = ''

    if p.menu_title:
      read_more_a_text = p.menu_title
    else:
      read_more_a_text = 'Continue reading'

    read_more_link = '<a class="post-continue-reading" href="' + p.url_path + '">' + read_more_a_text + ' &rarr;</a>'

    blog_posts_html += '<div class="post-listing">' + site.shortcodes['post_title'](site, p, '2') + excerpt + read_more_link + '</div>'

  blog_posts_html = '<div class="post-list">' + blog_posts_html + '</div>'
%>
${blog_posts_html}
