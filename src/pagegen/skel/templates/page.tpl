<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <base href="{{base_url}}" />
    <meta name="Generator" content="Pagegen" />
    <link rel="shortcut icon" href="{{base_url}}/include/images/favicon.ico" type="image/x-icon" />
    <link rel="stylesheet" href="https://pro.fontawesome.com/releases/v5.10.0/css/all.css" integrity="sha384-AYmEC3Yw5cVb3ZcuHtOA93w35dYTsvhLPVnYs9eStHfGJvOvKxVfELGroGkvsg+p" crossorigin="anonymous"/>
    <link rel="stylesheet" href="{{base_url}}/include/css/site.css" type="text/css" />
    <script src="{{base_url}}/include/javascript/site.js"></script>
  </head>
  <body>
    <div id="page" class="clearfix">
      <i class="fas fa-bars" id="hamburger" onclick="toggle_sidebar();"></i>
      <div id="sidebar">
        <a id="page_logo" href="{{base_url}}"><img src="{{base_url}}/include/images/pagegen_150x28.png" alt="Pagegen" /></a>
        <p id="blurb">Every page is a file<br /><span>Static site generator</span></p>
        <div id="menu">{{menu}}</div>
      </div><!-- /sidebar -->
      <article id="content">
        {{content}}
        <div id="footer">Copyright &#169; {{year}} &#8212; Generated by <a href="https://pagegen.phnd.net"><img src="{{base_url}}/include/images/pagegen_54x10.png" /></a></div>
      </article><!-- /content -->
    </div><!-- /page -->
    <script>
function toggle_sub_menu(i) {
  var ul = i.nextSibling;
  if (ul.style.display == 'block') {
    ul.style.display = 'none'
    i.className = toggle_show_sub_menu;
  }
  else {
    ul.style.display = 'block';
    i.className = toggle_hide_sub_menu;
  }
}


function show_current_page_parent_menues(obj) {
  console.log(obj);
  if (typeof obj === 'undefined') return;

  if (obj.id == 'menu') return;

  if (obj.parentElement.tagName == 'UL') {
    obj.parentElement.style.display = 'block';
  }

  show_current_page_parent_menues(obj.parentElement);
}


var uls = document.querySelectorAll('#menu ul');
var toggle_show_sub_menu = 'sub-menu-toggle fas fa-angle-down';
var toggle_hide_sub_menu = 'sub-menu-toggle fas fa-angle-up';


for (var i = 0; i < uls.length; i++) {

  if (uls[i].parentElement.tagName === 'LI') {

    uls[i].style.display = 'none'; // Hide sub menu

    // Create icon to toggle sub menu
    var toggle_icon = document.createElement('i');
    toggle_icon.className = toggle_show_sub_menu;
    toggle_icon.onclick = function(event){
      toggle_sub_menu(this);
    }

    uls[i].parentNode.insertBefore(toggle_icon, uls[i]);
  }
}


show_current_page_parent_menues(document.querySelectorAll('#pagegen-current-page')[0]);
    </script>
  </body>
</html>
