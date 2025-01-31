"""
Graphviz extensions for Markdown.
Renders the output inline, eliminating the need to configure an output
directory.

Supports outputs types of SVG and PNG. The output will be taken from the
filename specified in the tag.

Example:

<graphviz>dot attack_plan.svg
    digraph G {
        rankdir=LR
        Earth [peripheries=2]
        Mars
        Earth -> Mars
    }
</graphviz>

Requires the graphviz library (http://www.graphviz.org/) and python 3

Work heavily indebted to https://github.com/EricDuminil/markdown-inline-graphviz
"""

import re
import markdown
import subprocess
import base64
import shutil


BLOCK_RE_GRAPHVIZ_TAG = re.compile(
    r'^<graphviz>(?P<command>\w+)\s+(?P<filename>[^\s]+)\s*\n(?P<content>.*?)</graphviz>\s*$',
    re.MULTILINE | re.DOTALL)

# Command whitelist
SUPPORTED_COMMAMDS = ['dot', 'neato', 'fdp', 'sfdp', 'twopi', 'circo']


class InlineGraphvizExtension(markdown.Extension):

    def extendMarkdown(self, md):
        """ Add InlineGraphvizPreprocessor to the Markdown instance. """
        md.registerExtension(self)

        md.preprocessors.register(
            InlineGraphvizPreprocessor(md),
            'graphviz_block',
            30
        )


class InlineGraphvizPreprocessor(markdown.preprocessors.Preprocessor):

    def __init__(self, md):
        super(InlineGraphvizPreprocessor, self).__init__(md)

    def run(self, lines):
        """ Match and generate graphviz code blocks."""

        text = "\n".join(lines)
        while 1:
            m = BLOCK_RE_GRAPHVIZ_TAG.search(text)
            if m:
                command = m.group('command')

                # Check command exists on system
                if shutil.which(command) is None:
                    raise RuntimeError('<graphviz> tag found, but could not find "' + command + '", is graphviz installed?') 

                # Whitelist command, prevent command injection.
                if command not in SUPPORTED_COMMAMDS:
                    raise Exception('Command not supported: %s' % command)
                filename = m.group('filename')
                content = m.group('content')
                filetype = filename[filename.rfind('.')+1:]

                args = [command, '-T'+filetype]
                try:
                    proc = subprocess.Popen(
                        args,
                        stdin=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        stdout=subprocess.PIPE)
                    proc.stdin.write(content.encode('utf-8'))

                    output, err = proc.communicate()

                    if filetype == 'svg':
                        data_url_filetype = 'svg+xml'
                        encoding = 'utf-8'
                        full_svg_xml = output.decode(encoding)
                        img = ''

                        # Strip off xml doctype preamble, just want the svg tag
                        in_svg = False
                        for line in full_svg_xml.splitlines():
                            if line.startswith('<svg'):
                                in_svg = True

                            if in_svg:
                                img += line


                    if filetype == 'png':
                        data_url_filetype = 'png'
                        encoding = 'base64'
                        output = str(base64.b64encode(output), 'utf-8')
                        data_path = "data:image/%s;%s,%s" % (
                            data_url_filetype,
                            encoding,
                            output
                        )
                        img = '<img src="' + data_path + '" alt="' + filename + '" />'

                    text = '%s\n%s\n%s' % (
                        text[:m.start()], img, text[m.end():])

                except Exception as e:
                    err = str(e) + ' : ' + str(args)
                    return (
                        '<pre>Error : ' + err + '</pre>'
                        '<pre>' + content + '</pre>'
                    ).split('\n')

            else:
                break
        return text.split("\n")

def makeExtension(*args, **kwargs):
    return InlineGraphvizExtension(*args, **kwargs)
