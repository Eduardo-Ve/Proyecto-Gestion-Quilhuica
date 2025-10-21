document.addEventListener('DOMContentLoaded', function() {
    
    // --- Configuración ---
    // IDs por defecto que genera Django con form.as_p
    const rolesSelectId = 'id_roles';         
    const casetaFieldId = 'id_caseta_asignada'; // ID del *campo* select de caseta
    const rolQueOculta = 'Administrador';     // Texto del rol que oculta el campo
    // --- Fin Configuración ---

    const rolesSelect = document.getElementById(rolesSelectId);
    const casetaField = document.getElementById(casetaFieldId); // El campo <select> de caseta

    // 1. Validar que ambos campos existen en el formulario
    if (!rolesSelect || !casetaField) {
        console.warn("Script de roles/casetas no pudo encontrar 'id_roles' o 'id_caseta_asignada'.");
        return;
    }

    // 2. ¡Importante! Obtenemos el contenedor <p> padre del campo
    //    Esto es lo que realmente vamos a ocultar
    const casetaWrapper = casetaField.parentElement; 

    // --- Función Principal ---
    function toggleCasetaField() {
        // Obtenemos todas las opciones seleccionadas (funciona con selección múltiple)
        const selectedOptions = Array.from(rolesSelect.selectedOptions);
        
        // Vemos si alguna opción seleccionada es "Administrador"
        const isAdminSelected = selectedOptions.some(option => option.text === rolQueOculta);

        if (isAdminSelected) {
            // Ocultamos el <p> completo (que contiene el label y el select)
            casetaWrapper.style.display = 'none';
        } else {
            // Mostramos el <p> completo
            casetaWrapper.style.display = 'block';
        }
    }

    // 3. Llama a la función al cargar la página (por si el form viene con error y "Admin" ya está seleccionado)
    toggleCasetaField();

    // 4. Llama a la función CADA VEZ que el usuario cambie la selección de roles
    rolesSelect.addEventListener('change', toggleCasetaField);

});
// ya aqui comento para que sirve este codigo
// basicamente para evitar errores humanos el JS se va a encargar de que el usuario administrador, si va a crear otro admin
// no vaya a seleccionar por error que tiene una caseta asignada el admin