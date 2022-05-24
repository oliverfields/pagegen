<%inherit file="base.mako"/>

<%block name="content">
	<h1>${page.title}</h1>
	<ul>
	% for tag_name, tag in site.tags.items():
		<li><a href="${tag['url']}">${tag_name}</a></li>
	% endfor
	</ul>
</%block>

