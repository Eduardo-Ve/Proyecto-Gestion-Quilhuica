
document.addEventListener('DOMContentLoaded', function() {

    const rolesSelect = document.getElementById('id_roles');
    const casetasWrapper = document.getElementById('casetas-wrapper'); 
    // El contenedor <div> que creamos en el template

    if (!rolesSelect || !casetasWrapper) {
        console.warn("No se encontró id_roles o casetas-wrapper.");
        return;
    }

    function toggleCasetas() {
        const selectedText = rolesSelect.options[rolesSelect.selectedIndex].text;

        if (selectedText === "Encargado de Caseta") {
            casetasWrapper.style.display = "block"; // mostrar
        } else {
            casetasWrapper.style.display = "none"; // ocultar
        }
    }

    // Ejecutar al cargar
    toggleCasetas();

    // Ejecutar cuando cambia el rol
    rolesSelect.addEventListener('change', toggleCasetas);
});



