document.addEventListener('DOMContentLoaded', function() {

    const rolesSelect = document.getElementById('id_roles');
    const casetasWrapper = document.getElementById('casetas-wrapper'); 

    if (!rolesSelect || !casetasWrapper) {
        console.warn("No se encontró id_roles o casetas-wrapper.");
        return;
    }

    function toggleCasetas() {
        const selectedText = rolesSelect.options[rolesSelect.selectedIndex].text.trim();

        const rolesSinCasetas = ["Administrador"];  

        if (rolesSinCasetas.includes(selectedText)) {
            casetasWrapper.style.display = "none"; // ocultar para Admin
        } else {
            casetasWrapper.style.display = "block"; // mostrar para otros
        }
    }

    // Ejecutar al cargar la página
    toggleCasetas();

    // Ejecutar al cambiar el rol
    rolesSelect.addEventListener('change', toggleCasetas);
});
