<%inherit file="base.mako"/>

<%block name="content">
	<% 
		author = site.authors[page.headers['author']]
		social_html = ''
		size = '100'

		if 'social_links' in author.keys():
			links = author['social_links'].split(',')

			for link in links:
				if 'github.com' in link:
					link_name = 'Github'
				elif 'twitter.com' in link:
					link_name = 'Twitter'
				elif 'facebook.com' in link:
					link_name = 'Facebook'
				elif 'linkedin.com' in link:
					link_name = 'Linkedin'

				social_html += '<li><a href="' + link + '">' + link_name + '</a></li>'

			social_html = '<ul>' + social_html + '</ul>'

		if 'name' in author.keys():
			name = author['name']
		else:
			name = page.headers['author']

		if 'github_user' in author.keys():
			avatar = '<img src="https://github.com/' + author['github_user'] + '.png?size=' + size + '" alt="' + name + '" width="' + size + '" height="' + size + '" />'
		else:
			avatar = ''

		if 'blurb' in author.keys():
			blurb = author['blurb']
		else:
			blurb = ''
	%>
	<div class="author-full clearfix">
		${avatar}
		<p>${blurb}</p>
		${social_html}
	</div>

	<hr />

	<%
		pages_html = ''

		if 'pages' in author.keys() and len(author['pages']) > 0:

			for p in author['pages']:
				if 'description' in p.headers.keys() and p.headers['description']:
					description = p.headers['description']
				else:
					description = ''

				pages_html += '<p><strong><a href="' + p.url_path + '">' + p.title + '</a></strong><br />' + description + '</p>'
	%>
	${pages_html}
</%block>

