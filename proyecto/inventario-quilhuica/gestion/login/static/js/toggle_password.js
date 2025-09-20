// toggle_password.js

// Nos aseguramos de que el DOM esté completamente cargado antes de ejecutar el script
document.addEventListener("DOMContentLoaded", function () {
  // Referencias a los elementos del DOM
  const toggleBtn = document.getElementById("toggleBtn"); // El botón
  const passwordInput = document.getElementById("password"); // El input de contraseña
  const toggleIcon = document.getElementById("toggleIcon"); // El icono dentro del botón
  const toggleText = document.getElementById("toggleText"); // El texto dentro del botón

  // Escuchamos el click en el botón
  toggleBtn.addEventListener("click", () => {
    if (passwordInput.type === "password") {
      // Cambiamos el input a texto
      passwordInput.type = "text";

      // Cambiamos el icono
      toggleIcon.classList.remove("bi-eye-slash");
      toggleIcon.classList.add("bi-eye");

      // Cambiamos el texto
      toggleText.textContent = "Ocultar";
    } else {
      // Cambiamos el input a password
      passwordInput.type = "password";

      // Cambiamos el icono
      toggleIcon.classList.remove("bi-eye");
      toggleIcon.classList.add("bi-eye-slash");

      // Cambiamos el texto
      toggleText.textContent = "Mostrar";
    }
  });
});
