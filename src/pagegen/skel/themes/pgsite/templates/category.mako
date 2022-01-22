<%inherit file="base.mako"/>

<%block name="content">
	<ul>
	% for p in page.category_pages:
		<li><a href="${p.url_path}">${p.title}</a></li>
	% endfor
	</ul>
</%block>

