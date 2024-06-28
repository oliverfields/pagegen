"""
Markup a convo with speech bubbles

Example:

<convo>
{ thoughts
} nothing
<profile:<img src="/assets/mugshot.jpg" />
< Hei jeg er skoledagboka Starlet👋
>💖 hey
< Så hyggelig å møte deg😇 Kan jeg stille deg noen spørsmål?
>🫦 øh?
< Hvem er du forelsket i?
> Ruth-Iren er drit fin💩👰‍♀️
<💅💃😅 Nå vet Øyvind👺, Fred🥵 and Bendik🙄 dette
<😇 Hæ, sa du det til dem?
< Seff🙌
<🖕 Kanskje hun får vite det💖
<.
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

                profile_left = '<div class="convo-profile-left">🐘</div>'
                #profile_right = '<div class="convo-profile-right">🎠</div>'
                profile_right = ''
                profile_left_understanding = '<div class="convo-understanding-left">🐘</div>'

                for msg in m.group('msgs').split('\n'):
                    if msg:

                        if msg.startswith('<profile:'):
                            profile_left = '<div class="convo-profile-left">' + msg[9:] + '</div>'
                            profile_left_understanding = '<div class="convo-left-understanding">' + msg[9:] + '</div>'
                            continue

                        #if msg.startswith('>profile:'):
                        #    profile_right = '<div class="convo-profile-right">' + msg.lstrip[9:] + '</div>'
                        #    continue

                        if msg == 'left_here':
                            profile_left_understanding = ''
                            continue

                        parsed_msg = msg.split(' ', 1)
                        msg_meta = parsed_msg[0]
                        reaction_class_text = ' <span class="convo-msg-reaction">'
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
                            reactions = reactions.replace('convo-msg-reactions"> ' + reaction_class_text, 'convo-msg-reactions">')
                        except:
                            pass

                        try:
                            if msg_meta[1] == '.':
                                typing = True
                            else:
                                typing = False
                        except:
                            typing = False

                        if typing:
                            if source == '<':
                                html += '<div class="convo-typing-left">◗⬤◖</div>\n'
                            else:
                                html += '<div class="convo-typing-right">◗⬤◖</div>\n'
                        elif source == '<':
                            html += '<div class="convo-speech-left">' + profile_left + content + reactions + '</div>\n'
                        elif source == '>':
                            html += '<div class="convo-speech-right">' + profile_left_understanding + content + reactions + '</div>\n'
                        else:
                            html += msg + '\n'

                text = '%s\n%s\n%s' % (text[:m.start()], '<div class="convo">\n' + html + '</div>', text[m.end():])
            else:
                break

        return text.split("\n")


def makeExtension(*args, **kwargs):
    return InlineConvoExtension(*args, **kwargs)


