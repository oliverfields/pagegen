function addSearchForm() {
  // Get query string from url
  search_query_text = '';
  query_string = window.location.search.substring(1).split('&');
  for (let i = 0; i < query_string.length; i++) {
    let key_value = query_string[i].split('=');
    if(key_value[0] == 'q') {
      search_query_text = decodeURIComponent(key_value[1].replace(/\+/g, '%20'));
      break;
    }
  }

  // Create html search form
  const nav = document.getElementsByTagName('nav')[0];

  const form = document.createElement('form');
  form.setAttribute('action', '/search');
  form.setAttribute('class', 'search-form');
  form.setAttribute('method', 'GET');

  const query_field = document.createElement('input');
  query_field.setAttribute('type', 'text');
  query_field.setAttribute('name', 'q');
  query_field.setAttribute('id', 'search-query');
  query_field.setAttribute('class', 'control-field');
  query_field.setAttribute('placeholder', 'Search');
  query_field.setAttribute('required', '');
  query_field.setAttribute('value', search_query_text);

  const submit_query = document.createElement('input');
  submit_query.setAttribute('type', 'submit');
  submit_query.setAttribute('value', 'Go');
  submit_query.setAttribute('title', 'Search');
  submit_query.setAttribute('id', 'search-button');
  submit_query.setAttribute('class', 'control-button');

  // Make sure form only is submitted if it contains somethind
  form.onsubmit = function() {
    if(document.getElementById('search-query').value.length > 0) {
      return true;
    }
    return false;
  };

  form.appendChild(query_field);
  form.appendChild(submit_query);

  nav.appendChild(form);
}
addSearchForm();
