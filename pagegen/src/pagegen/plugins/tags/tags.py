class Plugin():

    def hook_pre_build(self, objects):
        print('pgn pre building tags dude')

    def hook_post_build(self, objects):
        i = objects['index']

        for url, p_meta in objects['index'].items():
            try:
                print(url + ': ' + p_meta['headers']['tags'])
            except KeyError:
                pass
