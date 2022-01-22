<%inherit file="base.mako"/>

<%block name="content">
	<ul>
	% for cat_name, category in categories.items():
		<li><a href="${category['url']}">${cat_name}</a></li>
	% endfor
	</ul>
</%block>

