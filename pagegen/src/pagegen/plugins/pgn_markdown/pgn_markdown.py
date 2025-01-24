import markdown
import markdown_inline_graphviz
import markdown_inline_convo


class Plugin():
    '''
    Convert page markdown content to html
    '''

    def pgn_hook_page_render_markup(self, objects):
        p = objects['page']

        try:
            md = markdown.Markdown(
                extensions = [
                    'tables',
                    'admonition',
                    markdown_inline_graphviz.makeExtension(),
                    markdown_inline_convo.makeExtension()
                ]
            )

            p.output = md.convert(p.body)
        except Exception as e:
            print(type(e))
            raise

