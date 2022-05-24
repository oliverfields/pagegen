<%inherit file="base.mako"/>

<%block name="content">
	<h1>${page.title}</h1>
	<ul>
	% for p in page.tag_pages:
		<li><a href="${p.url_path}">${p.title}</a></li>
	% endfor
	</ul>
</%block>

