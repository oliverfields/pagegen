<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <base href="${site.base_url}" />
    <link rel="canonical" href="${page.absolute_url}" />
    <meta name="copyright" content="Copyright &#169; ${year}" />
    ##<meta name="author" content="Oliver Fields">
    ##<meta name="contact" content="pagegen@phnd.net" />
    ## Open graph
    <meta name="Generator" content="Pagegen" />
    <link rel="apple-touch-icon" sizes="180x180" href="/assets/theme/favicon/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="/assets/theme/favicon/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/assets/theme/favicon/favicon-16x16.png">
    <link rel="manifest" href="/assets/theme/favicon/site.webmanifest">
    <link rel="mask-icon" href="/assets/theme/favicon/safari-pinned-tab.svg" color="#5bbad5">
    <link rel="shortcut icon" href="/assets/theme/favicon/favicon.ico">
    <meta name="msapplication-TileColor" content="#da532c">
    <meta name="msapplication-config" content="/assets/theme/favicon/browserconfig.xml">
    <meta name="theme-color" content="#ffffff">
    <link rel="stylesheet" href="/assets/theme/site.css" type="text/css" />
    ## schema.org
    % if page.headers['template'] == 'pages.mako':
      <%
          pd = page.headers['publish']
      %>
      <script type="application/ld+json">
      {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "${page.title}",
        "datePublished": "${pd}T06:00:00+01:00",
        "publisher": {
          "name": "Tides of Sea",
          "url": "https://tidesofsea.com"
        }
      }
      </script>
    % endif
  </head>
  <body>
    <header>
      <div class="logo">
        <a class="page-logo-link" href="${site.base_url}" aria-label="Site home">
        </a>
      </div>
      <nav>
      </nav>
    </header>
    <main>
      <%block name="content" />
    </main>
    <footer><hr />Copyright &#169; 2022 - ${year}</footer>
    <script src="/assets/theme/site.js"></script>
  </body>
</html>
