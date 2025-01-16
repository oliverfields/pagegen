<%inherit file="base.mako"/>
<%block name="content">
<%
archive = {}
mnames = {
"01": "January",
"02": "February",
"03": "March",
"04": "April",
"05": "May",
"06": "June",
"07": "July",
"08": "August",
"09": "September",
"10": "October",
"11": "November",
"12": "December"
}

# Find pages and append to archive dict
for p in site.page_list:
    # Only put posts in archive
    if p.headers['template'] == 'pages.mako' and p.headers['publish']:
        fyearmonth = p.headers['publish'][0:7]

        if not fyearmonth in archive.keys():
            archive[fyearmonth] = []

        archive[fyearmonth].append(p)

html = '<ol id="archive">'

# List archive contents
#for yearmonth, pages in archive.items():
for yearmonth in sorted(archive, reverse=True):
    html += '<li class="month"><span>' + mnames[yearmonth[5:7]] + ' ' + yearmonth[0:4] + '</span><ol class="posts">'

    for p in sorted(archive[yearmonth], key=lambda x: x.source_path, reverse=False):
        pretty_date = site.shortcodes['pretty_date'](site, p)
        pretty_date = pretty_date.split('</sup>', 1)[0] + '</sup>'

        html += '<li><span class="date">' + pretty_date + '</span> <a class="page-link" href="' + p.url_path + '">' + p.title + '</a></li>'

    html += '</ol>' # end posts
    html += '</li>' # end month

html += '</ol>' # end archive
%>
<h1 class="page-title">Archive</h1>
${html}
<script>
function toggleMonth(event) {
  var month = this.parentElement;
  var posts = month.getElementsByTagName('ol')[0];

  if (posts.style.display == 'none') {
    posts.style.display = 'block';
    this.innerHTML = this.innerHTML.replace(up, down);
  }
  else {
    posts.style.display = 'none';
    this.innerHTML = this.innerHTML.replace(down, up);
  }
}

//const up = "▼";
//const down = "▲";
const up = "⊕";
const down = "⊖";

[...document.getElementsByClassName('month')].forEach(m => {

  // Setup list
  var month_title = m.getElementsByTagName('span')[0];
  month_title.addEventListener('click', toggleMonth);
  month_title.classList.add('clickable');
  month_title.innerHTML = up + ' ' + month_title.innerHTML;

  var posts = m.getElementsByTagName('ol')[0];
  posts.style.display = 'none';
});
</script>
</%block>
