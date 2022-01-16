function toggle_sidebar() {
  var m = document.getElementById('sidebar');
  var h = document.getElementById('hamburger');
  if(m.style.display === "block") {
    m.style.display="none";
    h.className="fas fa-bars"
    h.style.color="#000000";
  }
  else {
    m.style.display="block";
    h.className="fas fa-times";
    h.style.color="#ffffff";
  }
}

window.onresize = function() {
    var sidebar = document.getElementById('sidebar');
    if(window.innerWidth > 940) {
      if(sidebar.style.display != 'block') sidebar.style.display = 'block';
    }
    if(window.innerWidth <= 940) {
      if(sidebar.style.display = 'block') sidebar.style.display = 'none';
    }
};
