<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <base href="${site.base_url}" />
    <link rel="canonical" href="${page.absolute_url}" />
    <title>${page.title}</title>
    <%
        # Meta description
        if isinstance(page.headers['description'], str) > 0:
            meta_desc = '<meta name="description" content="' + page.headers['description'].replace('"', '&quot;') + '" />'
        else:
            meta_desc = ''

        # Keywords
        meta_keywords = ''
        for t in page.headers['tags']:
            meta_keywords += t + ', '

        if len(meta_keywords) > 1:
            meta_keywords = '<meta name="keywords" content="' + meta_keywords.strip(' ,') + '" />'
    %>
    ${meta_desc}
    ${meta_keywords}
    % if (page.headers['sitemap exclude']):
    <meta name="robots" content="noindex" />
    % endif
    <meta name="copyright" content="Copyright &#169; ${year}" />
    ##<meta name="author" content="Oliver Fields">
    ##<meta name="contact" content="pagegen@phnd.net" />
    ## Open graph
    <%
        if 'og image' in page.custom_headers.keys():
            og_image_url = page.custom_headers['og image']



            # TODO update to automatically get stuff

            og_image_width = 400 # Need to get this value
            og_image_height = 400 # Need to get this value
            og_image_alt = 'Tides of Sea' 
            og_image_type = 'image/svg'
        else:
            og_image_url = site.base_url + '/assets/theme/hero.png'
            og_image_width = 1200
            og_image_height = 630
            og_image_alt = 'Tides of Sea'
            og_image_type = 'image/png'
    %>
    <meta property="og:image" content="${og_image_url}"/>
    <meta property="og:image:secure_url" content="${og_image_url}"/>
    <meta property="og:image:width" content="${og_image_width}"/>
    <meta property="og:image:height" content="${og_image_height}"/>
    <meta property="og:image:alt" content="${og_image_alt}"/>
    <meta property="og:image:type" content="${og_image_type}"/>
    <meta property="og:site_name" content="Tides of Sea"/>
    <meta property="og:title" content="${page.title}"/>
    <meta property="og:url" content="${page.absolute_url}"/>
    <meta property="og:type" content="website"/>
    % if page.headers['description']:
    <meta property="og:description" content="${page.headers['description']}"/>
    <meta name="description" content="${page.headers['description']}" />
    % endif
    ## End Open graph
    <link rel="alternate" type="application/rss+xml" title="${site.rss_title}" href="/feed.rss">
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
% if site.environment == 'prod':
    ## Piwik script
    <script>
## Allow user to set query string variable "no-tracking=enabled" in url, if set disable piwik tracking on device
var queryStrings;
(window.onpopstate = function () {
  var match,
    pl   = /\+/g,  // Regex for replacing addition symbol with a space
    search = /([^&=]+)=?([^&]*)/g,
    decode = function (s) { return decodeURIComponent(s.replace(pl, " ")); },
    query  = window.location.search.substring(1);

  queryStrings = {};
  while (match = search.exec(query))
     queryStrings[decode(match[1])] = decode(match[2]);
})();

if(queryStrings['tracking'] == 'off') {
  if(localStorage.getItem('tracking') != 'off') {
    localStorage.setItem('tracking', 'off');
    alert('Tracking is now turned off for this device🙈');
  }
}

if(queryStrings['tracking'] == 'on') localStorage.removeItem('tracking');


if (localStorage.getItem('tracking') != 'off') {

(function(window, document, dataLayerName, id) {
window[dataLayerName]=window[dataLayerName]||[],window[dataLayerName].push({start:(new Date).getTime(),event:"stg.start"});var scripts=document.getElementsByTagName('script')[0],tags=document.createElement('script');
function stgCreateCookie(a,b,c){var d="";if(c){var e=new Date;e.setTime(e.getTime()+24*c*60*60*1e3),d="; expires="+e.toUTCString();f="; SameSite=Strict"}document.cookie=a+"="+b+d+f+"; path=/"}
var isStgDebug=(window.location.href.match("stg_debug")||document.cookie.match("stg_debug"))&&!window.location.href.match("stg_disable_debug");stgCreateCookie("stg_debug",isStgDebug?1:"",isStgDebug?14:-1);
var qP=[];dataLayerName!=="dataLayer"&&qP.push("data_layer_name="+dataLayerName),isStgDebug&&qP.push("stg_debug");var qPString=qP.length>0?("?"+qP.join("&")):"";
tags.async=!0,tags.src="https://cuttingslack.containers.piwik.pro/"+id+".js"+qPString,scripts.parentNode.insertBefore(tags,scripts);
!function(a,n,i){a[n]=a[n]||{};for(var c=0;c<i.length;c++)!function(i){a[n][i]=a[n][i]||{},a[n][i].api=a[n][i].api||function(){var a=[].slice.call(arguments,0);"string"==typeof a[0]&&window[dataLayerName].push({event:n+"."+i+":"+a[0],parameters:[].slice.call(arguments,1)})}}(i[c])}(window,"ppms",["tm","cm"]);
})(window, document, 'dataLayer', 'f29a9a4f-08fe-4131-94be-3efab9aec743');
}
else {
  console.log('Tracking is disabled on this device, /?tracking=on to enable');
  let notrack = document.createElement('a');
  notrack.setAttribute('href', '${page.url_path}?tracking=on');
  notrack.setAttribute('title', 'Enable tracking');
  notrack.setAttribute('class', 'no-tracking-alert');
  notrack.appendChild(document.createTextNode('🙈'));

  document.body.appendChild(notrack);
}
    </script>
% endif
    <header>
      <div class="logo">
        <a class="page-logo-link" href="${site.base_url}" aria-label="Site home">
          <% logo_svg = site.shortcodes['svg_symbols'](site, page, 'tidesofsea-logo') %>
          ${logo_svg}
        </a>
      </div>
      <nav>
         <a href="/tag">Tags</a> <a href="/archive${site.default_extension}">Archive</a> <a title="About" href="/about${site.default_extension}">About</a>
      </nav>
    </header>
    <main>
      <%block name="content" />
    </main>
    <footer><hr />Copyright &#169; 2022 - ${year}</footer>
    <script src="/assets/theme/site.js"></script>
  </body>
</html>
