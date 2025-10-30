const doc = document;
const menuOpen = doc.querySelector(".menu");
const menuClose = doc.querySelector(".close");
const overlay = doc.querySelector(".overlay");
const dropdownToggle = doc.getElementById("dropdown-toggle");
const dropdownMenu = doc.querySelector(".dropdown-menu");

// === MENÚ PRINCIPAL ===
if (menuOpen && overlay) {
  menuOpen.addEventListener("click", () => {
    overlay.classList.add("overlay--active");
  });
}

if (menuClose && overlay) {
  menuClose.addEventListener("click", () => {
    overlay.classList.remove("overlay--active");
  });
}

// === MENÚ DESPLEGABLE (Auditoría y alertas) ===
if (dropdownToggle && dropdownMenu) {
  dropdownToggle.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropdownMenu.classList.toggle("active");
  });

  // Cerrar si se hace clic fuera
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".dropdown")) {
      dropdownMenu.classList.remove("active");
    }
  });
}
