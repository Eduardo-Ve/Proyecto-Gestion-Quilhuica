// static/js/toggle_form_fields.js

document.addEventListener('DOMContentLoaded', function() {
    // --- Lógica para la Categoría ---

    // 1. Selecciona el checkbox y los campos a ocultar
    const categoryCheckbox = document.getElementById('id_create_new_category');
    // Asumimos que crispy-forms envuelve el campo y su label en un div.
    // Buscamos los divs que contienen los campos 'new_category_name' y 'new_category_description'
    const newCategoryNameField = document.getElementById('div_id_new_category_name');
    const newCategoryDescriptionField = document.getElementById('div_id_new_category_description');

    // --- Lógica para la Presentación ---

    // 1. Selecciona el checkbox y los campos a ocultar
    const presentationCheckbox = document.getElementById('id_create_new_presentation');
    const packageTypeField = document.getElementById('div_id_package_type');
    const contentValueField = document.getElementById('div_id_content_value');
    const contentUnitField = document.getElementById('div_id_content_unit');

    // Función para actualizar la visibilidad de los campos
    function toggleVisibility(checkbox, fields) {
        if (checkbox.checked) {
            fields.forEach(field => field.style.display = 'block'); // Muestra los campos
        } else {
            fields.forEach(field => field.style.display = 'none');  // Oculta los campos
        }
    }

    // Comprueba el estado inicial al cargar la página y oculta los campos
    toggleVisibility(categoryCheckbox, [newCategoryNameField, newCategoryDescriptionField]);
    toggleVisibility(presentationCheckbox, [packageTypeField, contentValueField, contentUnitField]);


    // Añade un 'event listener' para que reaccione a los clics
    categoryCheckbox.addEventListener('change', function() {
        toggleVisibility(this, [newCategoryNameField, newCategoryDescriptionField]);
    });

    presentationCheckbox.addEventListener('change', function() {
        toggleVisibility(this, [packageTypeField, contentValueField, contentUnitField]);
    });
});