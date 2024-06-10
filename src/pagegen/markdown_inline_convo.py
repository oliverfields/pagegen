"""
Markup a convo with speech bubbles

Example:

<convo>
< Burger
> Bestill på padden
< Brus
> Bestill på padden
< Får dere mye tips her eller👄🫦
> Hæææ🤬
< 🤯😱😰🥵🥵🥵🥵🥵
> Idiot!
</convo>
"""

import re
import markdown



class InlineConvoExtension(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        """ Add InlineConvoPreprocessor to the Markdown instance. """
        md.registerExtension(self)
        md.preprocessors.add('convo', InlineConvoCompiler(md), "_begin")


class InlineConvoCompiler(markdown.preprocessors.Preprocessor):

    def __init__(self, md):
        super(InlineConvoCompiler, self).__init__(md)

    def run(self, lines):
        """ Match and generate convo html """

        CONVO_RE_QUESTION = re.compile(
            r'^<convo>\n(?P<msgs>.*?)</convo>$',
            re.MULTILINE | re.DOTALL
        )

        text = "\n".join(lines)

        while 1:
            m = CONVO_RE_QUESTION.search(text)
            html = ''
            if m:
                for msg in m.group('msgs').split('\n'):
                    if msg:
                        parsed_msg = msg.split(' ', 1)
                        prefix = parsed_msg[0]
                        content = parsed_msg[1]

                        if prefix == '<':
                            html += '<div class="convo-speech-left">' + content + '</div>\n'
                        elif prefix == '>':
                            html += '<div class="convo-speech-right">' + content + '</div>\n'
                        else:
                            html += msg + '\n'

                text = '%s\n%s\n%s' % (text[:m.start()], '<div class="convo">\n' + html + '</div>', text[m.end():])
            else:
                break

        return text.split("\n")


def makeExtension(*args, **kwargs):
    return InlineConvoExtension(*args, **kwargs)


