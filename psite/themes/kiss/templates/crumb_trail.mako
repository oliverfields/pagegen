<%page args = "page, site" />
<%
    from os.path import sep, join, isfile, isdir
    from configparser import NoOptionError

    try:
        dir_index = site.conf.get('site', 'directory_index')
    except NoOptionError:
        dir_index = 'index.html'

    try:
        crumb_home_title = site.conf.get('site', 'home_title')
    except NoOptionError:
        crumb_home_title = 'Home'

    path_parts = page.source_path[len(site.content_dir):].split(sep)

    crumbs = ''

    path_parts = path_parts[1:len(path_parts)]

    if page.source_path.endswith(sep + dir_index):
        path_parts = path_parts[0:len(path_parts) - 2]
    else:
        path_parts = path_parts[0:len(path_parts) - 1]

    if page.source_path != join(site.content_dir, dir_index):

        for i in range(0, len(path_parts)):
            maybe_index = join(site.content_dir, sep.join(path_parts), dir_index)

            if isfile(maybe_index):
                p = site.index[maybe_index]
                crumbs = f'<li><a href="{p.relative_url}">{p.headers["title"]}</a></li>{crumbs}'

            path_parts.pop()

        crumbs = f'<ol><li><a href="/">{crumb_home_title}</a></li>{crumbs}</ol>'
%>
${crumbs}
