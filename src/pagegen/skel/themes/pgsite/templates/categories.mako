<%inherit file="base.mako"/>

<%block name="content">
	<h1>${page.title}</h1>
	<ul>
	% for cat_name, category in site.categories.items():
		<li><a href="${category['url']}">${cat_name}</a></li>
	% endfor
	</ul>
</%block>

