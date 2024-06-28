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
                        msg_meta = parsed_msg[0]
                        reaction_class_text = ' <span class="convo-reaction">'
                        source = msg_meta[0]

                        try:
                            content = parsed_msg[1]
                        except:
                            content = ''

                        reactions = ''
                        try:
                            for c in  msg_meta[1:]:
                                reactions += reaction_class_text + c + '</span>'
                            reactions = '<div class="convo-msg-reactions">' + reactions + '</span></div>'
                            reactions = reactions.replace('convo_msg_reactions"> ' + reaction_class_text, 'convo_msg_reactions">')
                        except:
                            pass

                        try:
                            if msg_meta[1] == '.':
                                typing = True
                        except:
                            typing = False

                        if typing:
                            if source == '<':
                                html += '<div class="convo-typing-left">&ellip;</div>\n'
                            else:
                                html += '<div class="convo-typing-right">&ellip;</div>\n'
                        elif source == '<':
                            html += '<div class="convo-speech-left">' + content + reactions + '</div>\n'
                        elif source == '>':
                            html += '<div class="convo-speech-right">' + content + reactions + '</div>\n'
                        else:
                            html += msg + '\n'

                text = '%s\n%s\n%s' % (text[:m.start()], '<div class="convo">\n' + html + '</div>', text[m.end():])
            else:
                break

        return text.split("\n")


def makeExtension(*args, **kwargs):
    return InlineConvoExtension(*args, **kwargs)


