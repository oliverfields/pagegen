<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <base href="${site.base_url}" />
    <link rel="canonical" href="${page.absolute_url}" />
    <title>${page.headers['title']}</title>
    <%
        # Meta description
        if 'description' in page.headers.keys() and isinstance(page.headers['description'], str) > 0:
            meta_desc = '<meta name="description" content="' + page.headers['description'].replace('"', '&quot;') + '" />'
        else:
            meta_desc = ''
    %>
    ${meta_desc}
    <link rel="alternate" type="application/rss+xml" title="${site.conf['rss']['title']}" href="/feed.rss">
    <meta name="Generator" content="Pagegen" />
    <link rel="shortcut icon" href="/theme/favicon.ico" type="image/x-icon" />
    <link rel="stylesheet" href="/theme/site.css" type="text/css" />
  </head>
  <body>
    <div id="content">
      <article>
        <h1>${page.headers['title']}</h1>
        <%block name="content" />
      </article>
      <footer>Copyright &#169; ${year}</footer>
    </div><!-- /content -->
    <div id="menu">
      <header>
        <a href="/index">
          <img width="120" height="66" src="/theme/pgn-logo.svg">
        </a>
        <h2>Every page is a file</h2>
        <em>Static site generator</em>
      </header>
      <menu>
        <li><a href="1">Link 1</a></li>
        <li><a href="2">Link 2</a></li>
      </menu>
    </div><!-- /menu -->
    <div id="menu-toggle">
      <svg id="menu-open" width="2rem" height="2rem" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M5 6.5H19V8H5V6.5Z" fill="#1F2328"/>
        <path d="M5 16.5H19V18H5V16.5Z" fill="#1F2328"/>
        <path d="M5 11.5H19V13H5V11.5Z" fill="#1F2328"/>
      </svg>
      <svg id="menu-close" style="display: none;" width="2rem" height="2rem" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path fill-rule="evenodd" clip-rule="evenodd" d="M12 10.9394L16.9697 5.96961L18.0304 7.03027L13.0606 12L18.0303 16.9697L16.9697 18.0304L12 13.0607L7.03045 18.0302L5.96979 16.9696L10.9393 12L5.96973 7.03042L7.03039 5.96976L12 10.9394Z" fill="#1F2328"/>
      </svg>
    </div><!-- /menu-toggle -->
    <script src="/theme/site.js"></script>
  </body>
</html>
