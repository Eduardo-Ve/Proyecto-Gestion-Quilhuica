document.addEventListener("DOMContentLoaded", () => {
  const warehouseSelect = document.getElementById("id_ware");
  const addFormButton = document.getElementById("add-product-form");
  const formContainer = document.getElementById("product-forms-container");
  const emptyFormTemplate = document.getElementById("empty-form").cloneNode(true);
  const totalFormsInput = document.querySelector("#id_details-TOTAL_FORMS");

  emptyFormTemplate.removeAttribute("id");

  // 🔄 Cargar productos disponibles según caseta
  async function loadProducts(warehouseId) {
    const productSelects = document.querySelectorAll("select[name$='product']");
    if (!warehouseId) {
      productSelects.forEach((select) => {
        select.innerHTML = "<option value=''>Seleccione una caseta</option>";
      });
      return;
    }

    try {
      const response = await fetch(`/application/api/products/?warehouse_id=${warehouseId}`);
      const data = await response.json();

      if (data.products) {
        const options = data.products
          .map(
            (p) =>
              `<option value="${p.id}">
                ${p.name} (${p.presentation}) — Stock: ${p.stock}
              </option>`
          )
          .join("");

        productSelects.forEach((select) => {
          const currentValue = select.value;
          select.innerHTML = `<option value="">Seleccione un producto</option>${options}`;
          select.value = currentValue;
        });

        updateAvailableProducts();
      }
    } catch (error) {
      console.error("Error al cargar productos:", error);
    }
  }

  // 🚫 Evita duplicados en selects
  function updateAvailableProducts() {
    const allSelects = document.querySelectorAll("select[name$='product']");
    const selectedValues = Array.from(allSelects)
      .map((s) => s.value)
      .filter((v) => v);

    allSelects.forEach((select) => {
      const currentValue = select.value;
      Array.from(select.options).forEach((option) => {
        if (selectedValues.includes(option.value) && option.value !== currentValue && option.value !== "") {
          option.disabled = true;
          option.style.color = "#999";
        } else {
          option.disabled = false;
          option.style.color = "";
        }
      });
    });
  }

  // 🧹 Botón "Eliminar" con animación fade
  function addRemoveButtonListeners() {
    document.querySelectorAll(".form-row").forEach((row) => {
      // Evita duplicar botones
      if (!row.querySelector(".remove-form-btn")) {
        const deleteColumn = row.querySelector(".delete-column");
        if (deleteColumn) {
          deleteColumn.innerHTML = `
            <button type="button" class="btn btn-outline-danger remove-form-btn">
              <i class="bi bi-trash"></i> Eliminar
            </button>
          `;
        }
      }
    });

    // Evento de eliminación
    document.querySelectorAll(".remove-form-btn").forEach((btn) => {
      btn.onclick = (e) => {
        e.preventDefault();
        const formRow = btn.closest(".form-row");

        // Efecto fade-out
        formRow.style.transition = "opacity 0.3s ease";
        formRow.style.opacity = "0";

        setTimeout(() => {
          formRow.remove();
          // Actualizamos TOTAL_FORMS
          const forms = document.querySelectorAll(".form-row");
          totalFormsInput.value = forms.length;
          updateAvailableProducts();
        }, 300);
      };
    });
  }

  // ➕ Añadir nuevo producto
  addFormButton.addEventListener("click", () => {
    let formNum = parseInt(totalFormsInput.value);
    const newForm = emptyFormTemplate.cloneNode(true);
    newForm.innerHTML = newForm.innerHTML.replace(/__prefix__/g, formNum);
    newForm.style.display = "block";

    formContainer.appendChild(newForm);
    totalFormsInput.value = formNum + 1;

    // Cargar productos del almacén actual
    const currentWarehouse = warehouseSelect.value;
    if (currentWarehouse) {
      loadProducts(currentWarehouse);
    }

    addRemoveButtonListeners();
  });

  // 🔁 Detectar cambio en productos y caseta
  document.addEventListener("change", (e) => {
    if (e.target.name && e.target.name.endsWith("product")) {
      updateAvailableProducts();
    }
    if (e.target === warehouseSelect) {
      loadProducts(warehouseSelect.value);
    }
  });

  // Cargar productos al iniciar si ya hay caseta seleccionada
  if (warehouseSelect.value) {
    loadProducts(warehouseSelect.value);
  }

  addRemoveButtonListeners(); // <- ✅ se aplica al cargar la página
});