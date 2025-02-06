<%inherit file="base.mako"/>
<%block name="content">
<%
    page_list = ''
    for p in sorted(site.cache['tags'][page.headers['tag_key']]['pages'], key=lambda page: page['headers']['title']):
        page_list += f'<li><a href="{p["rel_url"]}">{p["headers"]["title"]}</a></li>\n'

    if len(page_list) > 0:
        content = '<ol>' + page_list + '</ol>'
    else:
        content = f'<em>No pages tagged {page.headers["tag_key"]}</em>'

%>
${content}
</%block>
