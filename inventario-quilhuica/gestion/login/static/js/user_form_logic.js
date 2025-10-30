


document.addEventListener('DOMContentLoaded', function() {
    // Buscar elementos por nombre si no se encuentran por ID
    const rolesSelect = document.querySelector('[id^="id_roles"], select[name*="roles"]');
    const casetaField = document.querySelector('[id^="id_caseta_asignada"], select[name*="caseta_asignada"]');

    if (!rolesSelect || !casetaField) {
        console.warn("Script no encontró los campos de roles o caseta_asignada.");
        return;
    }

    const casetaWrapper = casetaField.closest('p, div') || casetaField.parentElement;

    function toggleCasetaField() {
        const selectedOptions = Array.from(rolesSelect.selectedOptions);
        const isAdminSelected = selectedOptions.some(opt => opt.text.includes("Administrador"));
        casetaWrapper.style.display = isAdminSelected ? 'none' : 'block';
    }

    toggleCasetaField();
    rolesSelect.addEventListener('change', toggleCasetaField);
});



