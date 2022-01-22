<%inherit file="base.mako"/>

<%block name="content">
	<ol>
	% for c in page.children:
		<li><a href="${c.url_path}">${c.title}</a></li>
	% endfor
	</ol>
</%block>

