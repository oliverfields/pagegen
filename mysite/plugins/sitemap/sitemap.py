class Plugin():

    def pgn_hook_pre_build(self, site):
        print('hi my name is sitemap')

    def pgn_hook_post_build(self, site):
        print('bye my name was sitemap')
