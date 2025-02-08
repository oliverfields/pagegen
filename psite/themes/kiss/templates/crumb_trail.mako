<%page args = "page, site" />
<%
    from os.path import sep

    dir_index = site.conf.get('site', 'directory_index')

    path_parts = page.source_path[len(site.content_dir):].split(sep)

    print(path_parts)
    path_part_count = len(path_parts)

    if path_part_count > 1:
        for i in range(path_part_count - 1, 0, -1):
            #print('i: ' + str(i))
            for n in range(1, i + 1):
                print(path_parts[n] + sep, end='')
            print()

    crumbs = 'yeh'
%>
${crumbs}
