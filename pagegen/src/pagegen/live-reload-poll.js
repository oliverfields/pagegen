var sleep = time => new Promise(resolve => setTimeout(resolve, time))
var poll = (promiseFn, time) => promiseFn().then(
  sleep(time).then(() => poll(promiseFn, time))
)

var page_loaded_at = new Date();
var url = 'http://localhost:8000/pagegen_site_hash';
console.log(url)
var poll_intervall = 1000 // ms

poll(() => new Promise(() => {
  var http = new XMLHttpRequest();
  http.open('HEAD', url);
  http.onreadystatechange = function() {
    if (this.readyState == this.DONE) {
      var last_modified = new Date(this.getResponseHeader("Last-Modified"));
      console.log(url + ' modified ' + last_modified);
      if (last_modified > page_loaded_at) {
        window.location.reload();
      }
    }
  };
  http.send();
}), poll_intervall)
