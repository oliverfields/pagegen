<%inherit file="base.mako"/>
<%block name="content">
	% if page.toc:
		<ol id="toc">
		% for t in page.toc:
			% if t['level'] < 4:
				<li class="toc-h${t['level']}"><a href="#${t['id']}">${t['title']}</a></li>
			% endif
		% endfor
		</ol>
	% endif
	${page.html}
</%block>
