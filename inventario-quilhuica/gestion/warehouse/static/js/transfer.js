document.addEventListener('DOMContentLoaded', () => {
  const formsetContainer = document.getElementById('formset-container');
  const addButton = document.getElementById('add-form');
  const totalFormsInput = document.getElementById('id_form-TOTAL_FORMS');
  const template = document.getElementById('empty-form-template');
  const wareOriginSelect = document.getElementById('id_ware_origin');
  const wareDestinSelect = document.getElementById('id_ware_destin');
  const wareAlert = document.getElementById('same-ware-alert');
  const saveButton = document.querySelector('button[type="submit"], .btn-success');

  let productsCache = {};
  let lastWarehouseId = null;

  // ============================================================
  // 🔹 VALIDACIÓN: NO PERMITIR MISMA CASETA
  // ============================================================
  function validateWarehouses() {
    if (!wareOriginSelect || !wareDestinSelect) return;

    const origin = wareOriginSelect.value;
    const destin = wareDestinSelect.value;

    if (origin && destin && origin === destin) {
      // Mostrar alerta visual
      if (wareAlert) wareAlert.classList.remove('d-none');
      wareDestinSelect.value = '';
      wareDestinSelect.classList.add('is-invalid');

      // Desactivar botón guardar
      if (saveButton) saveButton.disabled = true;
    } else {
      // Ocultar alerta y limpiar estilo
      if (wareAlert) wareAlert.classList.add('d-none');
      wareDestinSelect.classList.remove('is-invalid');

      // Reactivar botón guardar si todo ok
      if (saveButton) saveButton.disabled = false;
    }
  }

  if (wareOriginSelect && wareDestinSelect) {
    wareOriginSelect.addEventListener('change', validateWarehouses);
    wareDestinSelect.addEventListener('change', validateWarehouses);
  }

  // ============================================================
  // 🔹 FUNCIÓN PARA CARGAR PRODUCTOS SEGÚN CASETA DE ORIGEN
  // ============================================================
  async function loadProductsForWarehouse(wareId) {
    const selects = document.querySelectorAll('.product-select');
    selects.forEach(s => {
      s.innerHTML = '<option value="">Cargando productos...</option>';
      s.disabled = true;
    });

    try {
      const resp = await fetch(`/warehouse/ajax/products/${wareId}/?t=${Date.now()}`);
      const data = await resp.json();
      productsCache = {};
      data.forEach(p => {
        productsCache[p.id] = p;
      });
    } catch (error) {
      console.error('Error al cargar productos:', error);
    } finally {
      selects.forEach(s => {
        populateSelect(s);
        s.disabled = false;
      });
    }
  }

  // ============================================================
  // 🔹 RELLENAR SELECT CON PRODUCTOS DISPONIBLES
  // ============================================================
  function populateSelect(selectEl) {
    const selectedValues = new Set(
      Array.from(document.querySelectorAll('.product-select'))
        .map(s => s.value)
        .filter(v => v)
    );

    const currentValue = selectEl.value;
    selectEl.innerHTML = '<option value="">Seleccione un producto</option>';

    Object.values(productsCache).forEach(p => {
      if (!selectedValues.has(String(p.id)) || String(p.id) === currentValue) {
        const opt = document.createElement('option');
        opt.value = p.id;
        opt.textContent = p.display_name;       
        selectEl.appendChild(opt);
      }
    });

    if (currentValue && productsCache[currentValue]) {
      selectEl.value = currentValue;
    }
  }

  // ============================================================
  // 🔹 MOSTRAR PRESENTACIÓN Y CANTIDAD DISPONIBLE
  // ============================================================
  function updatePresentation(selectElement) {
    const productId = selectElement.value;
    const formRow = selectElement.closest('.product-form');
    const presentationText = formRow.querySelector('.presentation-text');

    if (presentationText && productId && productsCache[productId]) {
      const p = productsCache[productId];
      presentationText.textContent = `Presentación: ${p.presentation} — Disponible: ${p.quantity} unidades`;
    } else if (presentationText) {
      presentationText.textContent = '';
    }
  }

  // ============================================================
  // 🔹 ACTUALIZAR TODOS LOS SELECTS AL CAMBIAR UNO
  // ============================================================
  function refreshAllSelects() {
    document.querySelectorAll('.product-select').forEach(populateSelect);
  }

  // ============================================================
  // 🔹 EVENTO: CAMBIO DE CASETA DE ORIGEN
  // ============================================================
  if (wareOriginSelect) {
    wareOriginSelect.addEventListener('change', async function () {
      const wareId = this.value;
      lastWarehouseId = wareId;

      document.querySelectorAll('.product-select').forEach(s => {
        s.innerHTML = '<option value="">Seleccione un producto</option>';
        updatePresentation(s);
      });

      if (wareId) {
        await loadProductsForWarehouse(wareId);
      } else {
        productsCache = {};
      }
    });
  }

  // ============================================================
  // 🔹 AGREGAR NUEVA FILA DE PRODUCTO
  // ============================================================
  if (addButton) {
    addButton.addEventListener('click', function () {
      if (!template) {
        console.error('¡No se encontró el <template id="empty-form-template">!');
        return;
      }

      const formNum = parseInt(totalFormsInput.value, 10);
      const html = template.innerHTML.replace(/__prefix__/g, formNum);
      const wrapper = document.createElement('div');
      wrapper.innerHTML = html;
      const newFormElem = wrapper.firstElementChild;

      formsetContainer.appendChild(newFormElem);
      totalFormsInput.value = formNum + 1;

      const select = newFormElem.querySelector('.product-select');
      populateSelect(select);
    });
  }

  // ============================================================
  // 🔹 EVENTOS DELEGADOS (SELECTS Y BOTONES)
  // ============================================================
  if (formsetContainer) {
    formsetContainer.addEventListener('change', e => {
      if (e.target.classList.contains('product-select')) {
        updatePresentation(e.target);
        refreshAllSelects();
      }
    });

    formsetContainer.addEventListener('click', e => {
      if (e.target.classList.contains('delete-btn')) {
        const formRow = e.target.closest('.product-form');
        if (!formRow) return;

        const deleteCheckbox = formRow.querySelector('input[type="checkbox"][name$="-DELETE"]');

        if (deleteCheckbox) {
          deleteCheckbox.checked = true;
          formRow.style.display = 'none';
        } else {
          formRow.remove();
        }

        refreshAllSelects();
      }
    });
  }

  // ============================================================
  // 🔹 CARGA INICIAL SI YA HAY CASETA SELECCIONADA
  // ============================================================
  if (wareOriginSelect && wareOriginSelect.value) {
    lastWarehouseId = wareOriginSelect.value;
    setTimeout(() => loadProductsForWarehouse(lastWarehouseId), 0);
  }
});
