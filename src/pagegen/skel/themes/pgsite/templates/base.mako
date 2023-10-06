<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${page.title}</title>
    <base href="${site.base_url}" />
    <meta name="Generator" content="pagegen.phnd.net" />
    <link rel="shortcut icon" href="${site.base_url}/assets/theme/images/favicon.ico" type="image/x-icon" />
    <link rel="stylesheet" href="https://pro.fontawesome.com/releases/v5.10.0/css/all.css" integrity="sha384-AYmEC3Yw5cVb3ZcuHtOA93w35dYTsvhLPVnYs9eStHfGJvOvKxVfELGroGkvsg+p" crossorigin="anonymous"/>
    <link rel="stylesheet" href="${site.base_url}/assets/theme/css/site.css" type="text/css" />
    <script src="${site.base_url}/assets/theme/javascript/site.js"></script>
  </head>
  <body>
    <div id="page" class="clearfix">
      <i class="fas fa-bars" id="hamburger" onclick="toggle_sidebar();"></i>
      <div id="sidebar">
        <a id="page_logo" href="${site.base_url}"><img src="${site.base_url}/assets/theme/images/pagegen_150x28.png" alt="Pagegen" /></a>
        <p id="blurb">Every page is a file<br /><span>Static site generator</span></p>
        <div id="search-form">
          <form action="${site.base_url}/search.html" method="GET">
            <input type="text" id="search-query" name="q" />
            <input type="submit" id="search-submit" value="Search" />
          </form>
        </div>
        <% menu = site.shortcodes['menu'](site, page) %>
        <div id="menu">${page.menu}</div>
      </div><!-- /sidebar -->
      <article id="content">
        <h1>${page.title}</h1>
        <%block name="content" />
        <div id="footer">Copyright &#169; ${year} &#8212; Generated by <a href="https://pagegen.phnd.net"><img src="${site.base_url}/assets/theme/images/pagegen_54x10.png" /></a></div>
      </article><!-- /content -->
    </div><!-- /page -->
    <script>
function toggle_sub_menu(i) {
  var ol = i.nextSibling;
  if (ol.style.display == 'block') {
    ol.style.display = 'none'
    i.className = toggle_show_sub_menu;
  }
  else {
    ol.style.display = 'block';
    i.className = toggle_hide_sub_menu;
  }
}


function show_current_page_parent_menues(obj) {
  if (typeof obj === 'undefined') return;

  if (obj.id == 'menu') return;

  if (obj.parentElement.tagName == 'OL') {
    obj.parentElement.style.display = 'block';
  }

  show_current_page_parent_menues(obj.parentElement);
}


var ols = document.querySelectorAll('#menu ol');
var toggle_show_sub_menu = 'sub-menu-toggle fas fa-angle-down';
var toggle_hide_sub_menu = 'sub-menu-toggle fas fa-angle-up';


for (var i = 0; i < ols.length; i++) {

  if (ols[i].parentElement.tagName === 'LI') {

    ols[i].style.display = 'none'; // Hide sub menu

    // Create icon to toggle sub menu
    var toggle_icon = document.createElement('i');
    toggle_icon.className = toggle_show_sub_menu;
    toggle_icon.onclick = function(event){
      toggle_sub_menu(this);
    }

    ols[i].parentNode.insertBefore(toggle_icon, ols[i]);
  }
}


show_current_page_parent_menues(document.querySelectorAll('#pagegen-current-page')[0]);
    </script>
  </body>
</html>
