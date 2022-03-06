<%inherit file="base.mako"/>
<%block name="content">
	${page.html}
	<%include file="list_posts.mako" args="site=site, posts_dir='posts', max_posts_limit=10" /> 
</%block>
