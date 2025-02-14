class Plugin():

    def hook_page_render(self, objects):
        '''
        Add everything preceeding <!-- more --> to self.excerpt
        '''

        p = objects['page']

        maybe_excerpt = p.out.split('<!-- more -->', 1)

        if len(maybe_excerpt) == 2:
            p.excerpt = maybe_excerpt[0]
