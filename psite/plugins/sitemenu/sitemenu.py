from conf import conf

def to_html(d):
    for a, b in d.items():
        if isinstance(b, str):
            print('check file exists')
            yield '<li><a href="{}">{}</a></li>'.format(a, b)
        elif isinstance(b, dict):
            yield '<li><span class="toggle-expand">{} <span>▼</span></span>\n<ol>\n{}</ol>\n</li>'.format(a, "\n".join(to_html(b)))

print(''' <html>
<head>
<style>
#site-menu ol {
display: none;
}
</style>
</head>
<body>
''')

print('<ol id="site-menu">' + '\n'.join(to_html(conf['menu'])) + '</ol>')

print('''
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
page_url = '/articles/web-server-tips';
let menuLinks = m.getElementsByTagName('A');
for (let i = 0; i < menuLinks.length; i++) {
  if (menuLinks[i].href == 'file://' + page_url) {
    show_current_page_parent_menus(menuLinks[i]);
  }
}
</script>
</body>
</html>''')
