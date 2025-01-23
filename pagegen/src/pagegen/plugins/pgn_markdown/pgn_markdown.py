class Plugin():

    def pgn_hook_page_generate_html(self, site, page):
        print('markdown ftw')
        page.html = 'seeexy'

    def pgn_hook_post_page_build(self, site, page):
        print('The page html has become ' + page.html)
