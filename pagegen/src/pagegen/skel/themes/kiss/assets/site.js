let menu = document.getElementById('menu');
let menuToggleDiv = document.getElementById('menu-toggle');
let menuOpen = document.getElementById('menu-open');
let menuClose = document.getElementById('menu-close');

menuToggleDiv.addEventListener('click', function (event) {
    // Toggle menu
    if (menu.classList.contains('menu-show')){
      menu.classList.remove('menu-show');
      menuOpen.style.display = 'block';
      menuClose.style.display = 'none';
    }
    else {
      menu.classList.add('menu-show');
      menuClose.style.display = 'block';
      menuOpen.style.display = 'none';
    }
});
