document.addEventListener('DOMContentLoaded', () => {
  const formsetContainer = document.getElementById('formset-container');
  const addButton = document.getElementById('add-form');
  const totalFormsInput = document.getElementById('id_form-TOTAL_FORMS');
  const template = document.getElementById('empty-form-template');
  const wareOriginSelect = document.getElementById('id_ware_origin');

  let productsCache = {};
  let lastWarehouseId = null;

  // ... (Tus funciones loadProductsForWarehouse, populateSelect, updatePresentation, refreshAllSelects están bien) ...
  
  // 🔹 Cargar productos desde el almacén seleccionado
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

  // 🔹 Rellenar el select con productos (solo los no seleccionados)
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
        opt.textContent = p.name;
        selectEl.appendChild(opt);
      }
    });

    if (currentValue && productsCache[currentValue]) {
      selectEl.value = currentValue;
    }
  }

  // 🔹 Mostrar presentación y cantidad disponible
  function updatePresentation(selectElement) {
    const productId = selectElement.value;
    const formRow = selectElement.closest('.product-form');
    // NOTA: Asegúrate de que tu `empty_form` también renderice '.presentation-text' si existe
    const presentationText = formRow.querySelector('.presentation-text'); 

    if (presentationText && productId && productsCache[productId]) {
      const p = productsCache[productId];
      presentationText.textContent = `Presentación: ${p.presentation} — Disponible: ${p.quantity} unidades`;
    } else if (presentationText) {
      presentationText.textContent = '';
    }
  }

  // 🔹 Actualizar todos los selects al cambiar uno (para ocultar productos ya usados)
  function refreshAllSelects() {
    document.querySelectorAll('.product-select').forEach(populateSelect);
  }

  // 🔹 Listener al cambiar el almacén de origen
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

  // 🔹 Agregar nueva fila de producto
  if (addButton) {
    addButton.addEventListener('click', function () {
      // Verificar que la plantilla exista
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
      // 'change' ya se maneja por delegación, no es necesario añadir más listeners
    });
  }

  // 🔹 Listener global para CAMBIOS y CLICKS (Delegación de eventos)
  if (formsetContainer) {
    formsetContainer.addEventListener('change', e => {
      // Delegación para el select de producto
      if (e.target.classList.contains('product-select')) {
        updatePresentation(e.target);
        refreshAllSelects();
      }
    });

    formsetContainer.addEventListener('click', e => {
      // Delegación para el botón de eliminar
      if (e.target.classList.contains('delete-btn')) {
        const formRow = e.target.closest('.product-form');
        if (!formRow) return;

        const deleteCheckbox = formRow.querySelector('input[type="checkbox"][name$="-DELETE"]');

        if (deleteCheckbox) {
          // Es un formulario existente: marcarlo para borrar y ocultarlo
          deleteCheckbox.checked = true;
          formRow.style.display = 'none';
        } else {
          // Es un formulario nuevo (del template): simplemente quitarlo del DOM
          formRow.remove();
        }
        
        // Actualizar selects para que el producto vuelva a estar disponible
        refreshAllSelects();
      }
    });
  }

  // 🔹 Carga inicial si ya hay un almacén seleccionado
  if (wareOriginSelect && wareOriginSelect.value) {
    lastWarehouseId = wareOriginSelect.value;
    setTimeout(() => loadProductsForWarehouse(lastWarehouseId), 0);
  }
});