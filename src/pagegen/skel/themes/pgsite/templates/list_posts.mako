<%page args = "site, posts_dir, max_posts_limit" />
<%
	blog_posts_html = ''
	posts = []
	counter = 0

	#sorted_pages = sorted(site.page_list, key=lambda d: d.headers['publish'], reverse=True)

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

		blog_posts_html += '<li>' + p.headers['publish'] + ' <a href="' + p.url_path + '">' + p.title + '</a>' + excerpt + '</li>'

	blog_posts_html = '<ol>' + blog_posts_html + '</ol>'
%>
${blog_posts_html}
