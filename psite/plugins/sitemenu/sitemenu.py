from conf import conf

def to_html(d, c = 0):
    for a, b in d.items():
        if isinstance(b, str):
            print('check file exists')
            yield '{}<li><a href="{}">{}</a></li>'.format('   '*c, a, b)
        elif isinstance(b, dict):
            yield '{}<li class="toggle-expand">{} -'.format('   '*c, a)
            yield '{}<ul>\n{}\n{}</ul></li>'.format('   '*c, "\n".join(to_html(b, c + 1)), '   '*c)

print('<ul>' + '\n'.join(to_html(conf['menu'])) + '</ul>')


#import pprint
#pprint.pprint(conf)
