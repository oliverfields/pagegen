<%inherit file="base.mako"/>
<%block name="content">
<%
    def get_pages_count(p):
        return len(p[1]['pages'])

    content = ''
    for p, data in dict(sorted(site.cache['tags'].items(), key=get_pages_count, reverse=True)).items():
        content += f'<li><a href="{data["rel_url"]}">{data["title"]}<span>{len(data["pages"])}</span></a></li>\n'
%>
<ol>
${content}
</ol>
</%block>
