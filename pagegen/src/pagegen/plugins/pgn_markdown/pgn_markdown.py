import markdown
import markdown_inline_graphviz
import markdown_inline_convo


class Plugin():
    '''
    Convert page markdown content to html
    '''

    def hook_page_render(self, objects):
        p = objects['page']

        # Pages may use render markup: false header to skip rendering
        if 'render markup' in p.headers.keys() and not p.headers['render markup']:
            return

        md = markdown.Markdown(
            extensions = [
                'tables',
                'admonition',
                markdown_inline_graphviz.makeExtension(),
                markdown_inline_convo.makeExtension()
            ]
        )

        p.out = md.convert(p.out)

