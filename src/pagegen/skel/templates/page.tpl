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
        {{menu}}
      </div><!-- /sidebar -->
      <article id="content">
        {{content}}
        <div id="footer">Copyright &#169; {{year}}</div>
      </article><!-- /content -->
    </div><!-- /page -->
  </body>
</html>
