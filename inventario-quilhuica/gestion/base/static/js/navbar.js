const doc = document;
const menuOpen = doc.querySelector(".menu");
const menuClose = doc.querySelector(".close");
const overlay = doc.querySelector(".overlay");
const dropdownToggle = document.getElementById('dropdown-toggle');
const dropdownMenu = document.querySelector('.dropdown-menu');

menuOpen.addEventListener("click", () => {
  overlay.classList.add("overlay--active");
});

menuClose.addEventListener("click", () => {
  overlay.classList.remove("overlay--active");
});


dropdownToggle.addEventListener('click', (e) => {
    e.preventDefault(); // Evita que el enlace salte
    e.stopPropagation();
    dropdownMenu.classList.toggle('active');
});

// Cerrar si se hace clic fuera
document.addEventListener('click', (e) => {
    // Cierra si el clic no fue dentro del contenedor .dropdown
    if (!e.target.closest('.dropdown')) {
        dropdownMenu.classList.remove('active');
    }
});