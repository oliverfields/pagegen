<%page args="page_list"/>

<%include file="page-list-2.mako" args="page_list=page.tag_pages, **context.kwargs" />

<%
	directories = []
	pages = []

	for p in sorted(page_list, key=lambda i: i.title):
		if p.children:
			directories.append(p)
		else:
			pages.append(p)
%>

<ul class="directory-list">
% for p in directories:
	<li><a class="page-link" href="${p.url_path}">${p.title}</a> </li>
% endfor
</ul>

<ul class="page-list">
% for p in pages:
	<% pretty_date = site.shortcodes['pretty_date'](site, p) %>

	<li>
	<a class="page-link" href="${p.url_path}">${p.title}</a>
	<span class="date">${pretty_date}</span>
	</li>

% endfor
</ul>
