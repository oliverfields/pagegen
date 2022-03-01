<%inherit file="base.mako"/>

<%block name="content">
	<ul>
	% for id, author in site.authors.items():
		<% 
			if 'name' in author.keys():
				name = author['name']
			else:
				name = id
		%>
		<li><a href="${author['author_page']}">${name}</a></li>
	% endfor
	</ul>
</%block>

