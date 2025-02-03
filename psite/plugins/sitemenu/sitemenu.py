from conf import conf
from os.path import isfile, join, sep, isdir
import pagegen.logger_setup
import logging

logger = logging.getLogger('pagegen.' + __name__)

class Plugin():

    def to_html(self, d):
        '''
        Make html menu
        '''

        for a, b in d.items():
            if isinstance(b, str):
                p = join(self.content_dir, a.lstrip(sep))
                if not a in self.ignore and not isfile(p):
                    logger.warning(f'Menu item "{b}" does not exist: {p}')
                yield '<li><a href="{}">{}</a></li>'.format(a, b)
            elif isinstance(b, dict):
                yield '<li><span class="toggle-expand">{} <span>▼</span></span>\n<ol>\n{}</ol>\n</li>'.format(a, "\n".join(self.to_html(b)))


    def get_all_keys(self, dictionary):
        '''
        Recursively get all keys in a nested directory structure
        '''
        for key, value in dictionary.items():
            if type(value) is dict:
                yield from self.get_all_keys(value)
            else:
                yield (key, value)


    def hook_post_build_lists(self, objects):

        logger.info('Adding sitemenu to site.cache["sitemenu"]')
        self.content_dir = objects['site'].content_dir
        self.ignore = conf['ignore']
        self.menu = conf['menu']

        defined_keys = []
        for key, value in self.get_all_keys(self.menu):
            defined_keys.append(key)


        # Strip dirs
        content_file_list = []
        for i in objects['site'].content_dir_list:
            if not isdir(i):
                content_file_list.append(i)

        # Check for pages that are not defined in the menu
        for c_abs_path in content_file_list:
            c_rel_path = c_abs_path[len(self.content_dir):]
            if not c_rel_path in self.ignore:
                if not c_rel_path in defined_keys:
                    logger.warning('Page not defined in site menu: ' + c_rel_path)

            else:
                logger.info('Ignoring: ' + c_rel_path)


        menu = '<menu id="site-menu">' + '\n'.join(self.to_html(self.menu)) + '</menu>'

        menu += '''
<script>
function show_current_page_parent_menus(obj){
  if (typeof obj === 'undefined') return;
  if (obj.id == 'site-menu') return;
  if (obj.parentElement.tagName == 'OL') {
    obj.parentElement.style.display='block';
  }
  show_current_page_parent_menus(obj.parentElement);
}

let m = document.getElementById('site-menu');

// Add click event to toggle sub menus
let showHideLinks = m.getElementsByClassName('toggle-expand');
for (let i = 0; i < showHideLinks.length; i++) {
  showHideLinks[i].addEventListener("click", function() {
    for (const child of this.parentElement.children) {
      if (child.tagName == 'OL') {
        if (child.style.display == 'block') {
          this.children[0].innerHTML = '▼';
          child.style.display = 'none';
        }
        else {
          this.children[0].innerHTML = '▲';
          child.style.display = 'block';
        }
      }
    }
  });
}

// Show current page
page_url = window.location.pathname;
console.log(page_url);
let menuLinks = m.getElementsByTagName('A');
for (let i = 0; i < menuLinks.length; i++) {
  if ('/' + menuLinks[i].href.split('/').slice(3).join('/') == page_url) {
    show_current_page_parent_menus(menuLinks[i]);
  }
}
</script>
</body>
</html>'''
        objects['site'].cache[__name__] = menu
