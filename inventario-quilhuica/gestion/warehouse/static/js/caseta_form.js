// /static/dashboard/js/caseta_form.js
(function() {
  const container = document.getElementById('formset-container');
  const totalForms = document.getElementById('id_form-TOTAL_FORMS');
  const emptyTpl = document.getElementById('empty-form-template').innerHTML;
  const src = document.getElementById('empty-form-source');

  // 🧩 Utilidad: obtener índice siguiente
  function nextIndex() {
    return parseInt(totalForms.value, 10);
  }

  // 🧩 Crea una fila nueva (equipo)
  function buildRow(eqName = null, sect = null) {
    const i = nextIndex();
    const eqField = src.children[0].outerHTML.replaceAll('__prefix__', i);
    const scField = src.children[1].outerHTML.replaceAll('__prefix__', i);

    let html = emptyTpl
      .replace('__equipo_field__', eqField)
      .replace('__sectores_field__', scField);

    container.insertAdjacentHTML('beforeend', html);
    totalForms.value = i + 1;

    // Valores por defecto
    if (eqName) container.querySelector(`#id_form-${i}-nombre_equipo`).value = eqName;
    if (sect) container.querySelector(`#id_form-${i}-sectores_count`).value = sect;

    // Foco + scroll
    const newInput = container.querySelector(`#id_form-${i}-nombre_equipo`);
    if (newInput) newInput.focus();
    container.lastElementChild.scrollIntoView({ behavior: 'smooth' });
  }

  // 🗑️ Eliminar fila
  container.addEventListener('click', (e) => {
    if (e.target.classList.contains('btn-delete')) {
      const form = e.target.closest('.equipment-form');
      form.remove();
      totalForms.value = container.querySelectorAll('.equipment-form').length;
    }
  });

  // ➕ Agregar N equipos consecutivos
  const btnBulkAdd = document.getElementById('btn-bulk-add');
  if (btnBulkAdd && !btnBulkAdd.dataset.bound) {
    btnBulkAdd.dataset.bound = "true";
    btnBulkAdd.addEventListener('click', () => {
      const n = parseInt(document.getElementById('bulk-n').value || '0', 10);
      const sect = parseInt(document.getElementById('bulk-sect').value || '1', 10);
      if (n <= 0) return;

      const existingNames = Array.from(
        container.querySelectorAll('input[name$="-nombre_equipo"]')
      ).map(i => i.value.trim()).filter(Boolean);

      let startNum = 1;
      if (existingNames.length) {
        const last = existingNames[existingNames.length - 1];
        const match = last.match(/\d+$/);
        if (match) startNum = parseInt(match[0]) + 1;
      }

      for (let k = 0; k < n; k++) {
        const name = `Equipo ${startNum + k}`;
        buildRow(name, sect);
      }
    });
  }

  // ➕ Agregar 1 equipo rápido
  const btnAddOne = document.getElementById('btn-add-one');
  if (btnAddOne && !btnAddOne.dataset.bound) {
    btnAddOne.dataset.bound = "true";
    btnAddOne.addEventListener('click', () => {
      const sect = 1;
      const existingNames = Array.from(
        container.querySelectorAll('input[name$="-nombre_equipo"]')
      ).map(i => i.value.trim()).filter(Boolean);

      let nextNum = 1;
      if (existingNames.length) {
        const last = existingNames[existingNames.length - 1];
        const match = last.match(/\d+$/);
        if (match) nextNum = parseInt(match[0]) + 1;
      }

      const newName = `Equipo ${nextNum}`;
      buildRow(newName, sect);
    });
  }
})();
