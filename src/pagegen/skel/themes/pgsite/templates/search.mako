<%inherit file="base.mako"/>

<%block name="content">
<h1>Search</h1>

<div id="search"></div>

<script>
function hit_in_result(hit, result){
  for (var i=0;i<result.length;i++) {
    if (result[i].url == hit.url) {
      return true
    }
  }
  return false
}

function do_search(search_string) {
  query = search_string.toLowerCase().split(' ');
  result=[];
  fetch('/search-index.json')
  .then(response => response.json())
  .then(data => {
    for (var i=0;i<query.length; i++) {
      var term=query[i];
      if (typeof data.terms[term] !== 'undefined') {
        for (var x=0;x<data.terms[term].length; x++) {
          url_id=data.terms[term][x];
          hit={
            url:data.urls[url_id][0],
            title:data.urls[url_id][1],
            desc:data.urls[url_id][2]
          }
          if (hit_in_result(hit, result) == false) {
            result.push(hit);
          }
        }
      }
    }
    // Build result content
    if(result.length>0) {
      if(result.length == 1) {
        plural = '';
      }
      else {
        plural = 's'
      }
      html='<div id="hit-count">'+result.length+' result' + plural + '</div>';
      for (var n=0;n<result.length;n++) {
        html+='<div class="search-hit"><a href="'+result[n].url+'">'+result[n].title+'</a>'
        if (result[n].desc.length > 0) {
          html+='<p>'+result[n].desc+'</p>';
        }
        html+='</div>'
      }
    }
    else {
      html='<i>No hits</i>'
    }
    // Remove any old search results
    search_results = document.getElementById('search');
    while (search_results.firstChild) {
      search_results.removeChild(search_results.firstChild);
    }
    search_results.innerHTML = html;
  });
}

query_string = window.location.search.substring(1).split('&');
for (let i = 0; i < query_string.length; i++) {
  let key_value = query_string[i].split('=');
  if(key_value[0] == 'q') {
    //document.getElementById('search-query').value = key_value[1];
    do_search(key_value[1]);
    break;
  }
}
</script>
</%block>
