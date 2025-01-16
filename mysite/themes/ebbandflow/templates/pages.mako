<%inherit file="base.mako"/>
<%!
import urllib.parse
from pagegen.utility_no_deps import report_notice, report_warning, remove_prefix
%>
<%block name="content">
  <%
    # Print warning if no description

    try:
      desc_len = len(page.headers['description'])
      if desc_len < 120 or desc_len > 160:
        report_notice(remove_prefix(page.source_path, site.site_dir + '/') + ' description is ' + str(desc_len) + ' long, wich is outside optimal range (120-160)')
    except:
        report_warning(remove_prefix(page.source_path, site.site_dir + '/') + ' description not found')

    title = site.shortcodes['post_title'](site, page)
    try:
        tags = site.shortcodes['post_tags'](site, page)
    except:
        tags = False
    series = site.shortcodes['series'](site, page)
  %>
  <article>
    ${title}
    % if series != '':
      ${series}
    % endif
    <%
      # Remove comments from content
      html = ''
      for l in page.html.splitlines():
        if site.environment == 'prod':
          if not l.startswith('<p>// ') and not l.startswith('//'):
            html += l + '\n'
        else:
          if l.startswith('<p>// ') or l.startswith('//'):
            html += l.replace('// ', '<p style="color: var(--bg-secondary); font-style: italic;">//')
          else:
            html += l + '\n'

    %>
    ${html}
    % if tags != '':
      ${tags}
    % endif
    <%
      url_encoded_title = urllib.parse.quote(page.title, safe='')
      url_encoded_url = urllib.parse.quote(page.absolute_url, safe='')
    %>
    <div class="sharing">
      <a class="share-button" href="https://www.facebook.com/sharer/sharer.php?u=${url_encoded_url}" target="_blank">
        <% facebook_svg = site.shortcodes['svg_symbols'](site, page, 'facebook-logo') %>
        ${facebook_svg}
      </a>
      <a class="share-button" href="https://bsky.app/intent/compose?text=${url_encoded_title}%20${url_encoded_url}" target="_blank">
        <% bsky_svg = site.shortcodes['svg_symbols'](site, page, 'bsky-logo') %>
        ${bsky_svg}
      </a>
      <a class="share-button" href="https://twitter.com/share?text=${url_encoded_title}&url=${url_encoded_url}" target="_blank">
        <% twitter_svg = site.shortcodes['svg_symbols'](site, page, 'x-twitter-logo') %>
        ${twitter_svg}
      </a>
      <a class="share-button" href="https://www.reddit.com/submit?url=${url_encoded_url}&title=${url_encoded_title}" target="_blank">
        <% reddit_svg = site.shortcodes['svg_symbols'](site, page, 'reddit-logo') %>
        ${reddit_svg}
      </a>
    </div>
  </article>
  <div class="prev-next-links">
    <div class="previous-link">
    % if page.previous_page:
      <a href="${page.previous_page.url_path}">&larr; ${page.previous_page.title}</a>
    % endif
    </div><div class="next-link">
    % if page.next_page:
      <a href="${page.next_page.url_path}">${page.next_page.title} &rarr;</a>

    % endif
    </div>
  </div>
  <h2 class="comment-header">Comments</h2>
  <div id="cusdis_thread"
  data-host="https://cusdis.com"
  data-app-id="e30ceac9-c382-407e-856c-5503918d83ba"
  data-page-id="${page.url_path}"
  data-page-url="${page.absolute_url}"
  data-page-title="${page.title}"
  data-theme="auto"
></div>
##<script async defer src="https://cusdis.com/js/cusdis.es.js"></script>
<script async defer src="/assets/theme/cusdis.es.js"></script>
<script>
function iLoveMyMTV(element) {
  // Every link to youtube video gets option to play in popup window

  var popup = document.createElement('div');
  popup.className = 'popup';
  popup.style['background-color'] = 'green';
  popup.style.position = 'fixed';
  popup.style.top = '1em';
  popup.style.left = '1em';
  popup.style['z-index'] = '9999';
  popup.style.display = 'none';

  var popupBar = document.createElement('div');
  popupBar.className = 'popup-bar';

  var popupVideo = document.createElement('iframe');
  popupVideo.className = 'popup-video';
  popupVideo.width = '187';
  popupVideo.height = '105';
  //popupVideo.setAttribute('src', 'https://www.youtube.com/embed/XIg87UsTBOM?si=Pmx_pZMYcn_hJ41w');
  //title="YouTube video player"
  popupVideo.setAttribute('frameborder', '0');
  popupVideo.setAttribute('allow', 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share');
  popupVideo.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');
  popupVideo.setAttribute('allowfullscreen', true);

  var popupMove = document.createElement('div');
  popupMove.className = 'popup-move';
  popupMove.style.cursor = 'move';
  popupMove.style.width = '164px';
  popupMove.style['padding-left'] = '3px';
  popupMove.style.display = 'inline-block';

  popupMove.innerHTML = '😎 ❤️‍🔥 M 📺️ !';
  popupBar.appendChild(popupMove);

  var popupClose = document.createElement('div');
  popupClose.className = 'popup-close';
  popupClose.style.cursor = 'pointer';
  popupClose.style.float = 'right';
  popupClose.style['text-align'] = 'center';

  popupClose.innerHTML = '✕';
  popupClose.addEventListener('click', function(e){
    // 1 = Left mouse button
    if (e.which === 1) {
      popup.style.display = 'none'; 
      // Stop video if playing
      popupVideo.contentWindow.postMessage('{"event":"command","func":"pauseVideo","args":""}', '*')
    }
  }, false);

  popupBar.appendChild(popupClose);

  popup.appendChild(popupBar);
  popup.appendChild(popupVideo);

  window.onkeydown = function(e){
    if(e.keyCode == 27){ // if ESC key pressed
      popupClose.click(e);
    }
  }

  //-- let the popup make draggable & movable.
  var offset = { x: 0, y: 0 };

  popupBar.addEventListener('mousedown', mouseDown, false);
  window.addEventListener('mouseup', mouseUp, false);

  function mouseUp() {
    window.removeEventListener('mousemove', popupMoveXY, true);
  }

  function mouseDown(e) {
    offset.x = e.clientX - popup.offsetLeft;
    offset.y = e.clientY - popup.offsetTop;
    window.addEventListener('mousemove', popupMoveXY, true);
  }

  function popupMoveXY(e){
    //popup.style.position = 'absolute';
    var top = e.clientY - offset.y;
    var left = e.clientX - offset.x;
    popup.style.top = top + 'px';
    popup.style.left = left + 'px';
  }
  //-- / let the popup make draggable & movable.

  document.body.appendChild(popup);

  function toggleVideo(element) {
    var btn = document.createElement('span');
    btn.className = 'popup-open-button';
    btn.style['margin-left'] = '.5em';
    btn.style.cursor = 'pointer';
    btn.innerHTML = '📺️';

    var embedUrl = element.href.replace('/watch?v=', '/embed/') + '?autoplay=1&enablejsapi=1';

    btn.addEventListener('click', function() { popupVideo.setAttribute('src', embedUrl); popup.style.display = 'block'; });

    return btn;
  }

  // Find all links
  var links = element.getElementsByTagName('a');
  for(var i = 0; i< links.length; i++){

    // If a video link
    if (links[i].href.startsWith('https://www.youtube.com/') || links[i].href.startsWith('https://youtube.com')) {

      // Add popup button to link
      links[i].parentNode.insertBefore(
        toggleVideo(links[i]),
        links[i].nextSibling
      );
    }
  }
}

iLoveMyMTV(document.getElementsByTagName('article')[0]);
</script>
</%block>
