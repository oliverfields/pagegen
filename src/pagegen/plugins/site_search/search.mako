<%inherit file="base.mako"/>

<%block name="content">
<div id="search"></div>
<script>
window.addEventListener('DOMContentLoaded', () => {
  function addHit(data, result, urlIndex, exactMatch){
    // Add pages to search result

    let hit = {
      url: data.urls[urlIndex][0],
      title: data.urls[urlIndex][1],
      desc: data.urls[urlIndex][2],
      exactMatch: exactMatch
    }

    // Only add page if it is not already added
    let hitAlreadyAdded = false;
    result.forEach(alreadyAddedHit => {
      if(alreadyAddedHit.url == hit.url) {
        hitAlreadyAdded = true;
      }
    });
    if(hitAlreadyAdded == false) result.push(hit);
  }

  function doSearch(searchString) {
    searchQuery = searchString.replace('+', '%20');
    searchQuery = decodeURI(searchQuery);
    searchQuery = searchQuery.toLowerCase();

    searchQuery = searchQuery.split(' ');
    result = [];

    fetch('/site-search-index.json')
    .then(response => response.json())
    .then(data => {
      for (var i=0;i<searchQuery.length; i++) {
        var searchTerm = searchQuery[i];

        // Add hits that match exactly
        for(const [indexedTerm, urlsIndexes] of Object.entries(data.terms)) {
          if(searchTerm == indexedTerm) urlsIndexes.forEach(urlIndex => addHit(data, result, urlIndex, true));
        }

        // Add hits that only match start of term
        for(const [indexedTerm, urlsIndexes] of Object.entries(data.terms)) {
          if(indexedTerm.startsWith(searchTerm)) urlsIndexes.forEach(urlIndex => addHit(data, result, urlIndex, false));
        }
      }

      // Build result content
      if(result.length>0) {
        html='';
        for (var n=0;n<result.length;n++) {
          html+='<div class="search-hit"><a href="'+result[n].url+'">'+result[n].title+'</a>'
          if (result[n].desc.length > 0) {
            html+='<p>'+result[n].desc+'</p>';
          }
          html+='</div>'
        }
      }
      else {
        search_query_text = decodeURIComponent(searchString.replace(/\+/g, '%20'));
        html='<p>Nothing matches <q>' + search_query_text + '</q>, perhaps try a <a href="https://google.com/search?q=' + search_query_text + '%20site:${site.base_url}">Google site search</a>?</p>'
      }
      // Remove any old search results
      searchResults = document.getElementById('search');
      while (searchResults.firstChild) {
        searchResults.removeChild(searchResults.firstChild);
      }
      searchResults.innerHTML = html;
    });
  }

  queryString = window.location.search.substring(1).split('&');
  for (let i = 0; i < queryString.length; i++) {
    let key_value = queryString[i].split('=');
    if(key_value[0] == 'q') {
      document.getElementById('search-query').setAttribute('value', key_value[1]);
      doSearch(key_value[1]);
      break;
    }
  }
});
</script>
</%block>
