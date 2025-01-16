<%inherit file="base.mako"/>

<%block name="content">
	<h1 class="page-title">${page.title}</h1>
	<ul class="tag-overview-list">
	% for tag in sorted(site.tags.items(), key=lambda k: (-k[1]['page_count'], k[1]['name'])):
		<li><a href="${tag[1]['url']}">#${tag[0]}</a> <span class="counter">${tag[1]['page_count']}</span></li>
	% endfor
	</ul>
</%block>

