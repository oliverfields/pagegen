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
    % if ('sitemap exclude' in page.headers.keys() and page.headers['sitemap exclude']):
    <meta name="robots" content="noindex" />
    % endif
    <meta name="copyright" content="Copyright &#169; ${year}" />
    ##<meta name="author" content="Oliver Fields">
    ##<meta name="contact" content="pagegen@phnd.net" />
    ## Open graph
    <%
        if 'og image' in page.headers.keys():
            og_image_url = page.headers['og image']



            # TODO update to automatically get stuff

            og_image_width = 400 # Need to get this value
            og_image_height = 400 # Need to get this value
            og_image_alt = 'Pagegen'
            og_image_type = 'image/svg'
        else:
            og_image_url = site.base_url + '/assets/theme/hero.png'
            og_image_width = 1200
            og_image_height = 630
            og_image_alt = 'Pagegen'
            og_image_type = 'image/png'
    %>
    <meta property="og:image" content="${og_image_url}"/>
    <meta property="og:image:secure_url" content="${og_image_url}"/>
    <meta property="og:image:width" content="${og_image_width}"/>
    <meta property="og:image:height" content="${og_image_height}"/>
    <meta property="og:image:alt" content="${og_image_alt}"/>
    <meta property="og:image:type" content="${og_image_type}"/>
    <meta property="og:site_name" content="pagegen.phnd.net"/>
    <meta property="og:title" content="${page.headers['title']}"/>
    <meta property="og:url" content="${page.absolute_url}"/>
    <meta property="og:type" content="website"/>
    % if 'description' in page.headers.keys() and page.headers['description']:
    <meta property="og:description" content="${page.headers['description']}"/>
    <meta name="description" content="${page.headers['description']}" />
    % endif
    ## End Open graph
    <link rel="alternate" type="application/rss+xml" title="${site.conf['rss']['title']}" href="/feed.rss">
    <meta name="Generator" content="Pagegen" />
    <link rel="shortcut icon" href="${site.base_url}/theme/favicon.ico" type="image/x-icon" />
    <link rel="stylesheet" href="/theme/site.css" type="text/css" />
    <script async defer src="https://buttons.github.io/buttons.js"></script>
  </head>
  <body>
    <div id="content">
      <article>
        <%include file="crumb_trail.mako" args="site=site, page=page" />
        <h1>${page.headers['title']}</h1>
        <%block name="content" />
      </article>
      <footer>Copyright &#169; 2022 - ${year}</footer>
    </div><!-- /content -->
    <div id="menu">
      <header>
        <a href="/">
          <img width="120" height="66" src="/theme/pgn-logo.svg">
        </a>
        <h2>Every page is a file</h2>
        <em>Static site generator</em>
      </header>
      <div id="search-form">
        <form action="${site.base_url}/search-results" method="GET">
          <input type="text" id="search-query" name="q" />
          <input type="submit" id="search-submit" value="🔍️" />
        </form>
      </div><!-- /search-form -->
      ${site.cache['sitemenu']}
      <ol>
        <li>✉️ <a href="mailto:pagegen@phnd.net">pagegen@phnd.net</a></li>
        <li>🐞 <a href="https://github.com/oliverfields/pagegen_site/issues">Issue tracker</a></li>
      </ol>
      <div class="github-button-container"><a class="github-button" href="https://github.com/oliverfields/pagegen" data-show-count="true" data-size="large" aria-label="Star oliverfields/pagegen on GitHub">Star</a></div>

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
