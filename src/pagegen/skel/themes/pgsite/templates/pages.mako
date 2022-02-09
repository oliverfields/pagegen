<%inherit file="base.mako"/>
<%block name="content">
	% if page.toc:
		<ul>
		% for t in page.toc:
			% if t['level'] < 4:
				<li class="$t['level']"><a href="#${t['id']}">${t['title']}</a></li>
			% endif
		% endfor
		</ul>
	% endif
	${page.content_html}
</%block>
