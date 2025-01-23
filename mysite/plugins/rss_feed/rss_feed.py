class Plugin():

    def pgn_hook_pre_build(self, objects):
        objects['site'].title = 'cool'
        print('site pre building rss feed man')


    def pgn_hook_post_build(self, objects):
        print('site post building rss feed man')
