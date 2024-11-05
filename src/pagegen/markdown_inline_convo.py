"""
Markup a convo with speech bubbles

Example:

<convo>
[avatar]:<img src="/assets/mugshot.jpg" />
[name]:Left Name
< Hei jeg er skoledagboka Starlet👋
>💖 hey
< Så hyggelig å møte deg😇 Kan jeg stille deg noen spørsmål?
>🫦 øh?
< Hvem er du forelsket i?
> Ruth-Iren er drit fin💩👰‍♀️
<💅💃😅 Nå vet Øyvind👺, Fred🥵 and Bendik🙄 dette
{ Is this really happening to me?
<😇 Hæ, sa du det til dem?
< Seff🙌
[left_here]
<🖕 Kanskje hun får vite det💖
<.
[input]:Unsent message
</convo>
"""

import re
import markdown



class InlineConvoExtension(markdown.Extension):

    def extendMarkdown(self, md):
        """ Add InlineConvoPreprocessor to the Markdown instance. """
        md.registerExtension(self)
        md.preprocessors.register(InlineConvoCompiler(md), 'convo', 31)


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
                profile_left_avatar = ''
                profile_left = ''
                profile_left_understanding = ''
                profile_left_header = False
                input = ''

                for msg in m.group('msgs').split('\n'):
                    if msg:

                        if msg.startswith('[avatar]:'):
                            profile_left_avatar = msg[9:]
                            profile_left = '<div class="convo-profile-left">' + profile_left_avatar + '</div>'
                            profile_left_understanding = '<div class="convo-left-understanding">' + profile_left_avatar + '</div>'
                            continue

                        if msg.startswith('[name]:'):
                            html = '<div class="convo-header"><div class="convo-header-profile">' + profile_left_avatar + '</div><strong>' + msg[7:] + '</strong></div>'
                            continue

                        if msg.startswith('[input]:'):
                            input = '<div class="convo-input">' + msg[8:] + '<div class="convo-input-send">↲</div></div>'
                            continue

                        if msg == '[left_here]':
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
                        elif source == '{':
                            html += '<div class="convo-meta-left">' + content + reactions + '</div>\n'
                        elif source == '}':
                            html += '<div class="convo-meta-right">' + profile_left_understanding + content + reactions + '</div>\n'
                        else:
                            html += msg + '\n'

                text = '%s\n%s\n%s' % (text[:m.start()], '<div class="convo">\n' + html + input + '</div>', text[m.end():])
            else:
                break

        return text.split("\n")


def makeExtension(*args, **kwargs):
    return InlineConvoExtension(*args, **kwargs)


