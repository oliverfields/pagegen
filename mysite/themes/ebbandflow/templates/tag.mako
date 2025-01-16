<%inherit file="base.mako"/>
<%block name="content">
	<h1 class="page-title">#${page.title}</h1>
	<%include file="page-list.mako" args="page_list=page.tag_pages, **context.kwargs" />
</%block>

