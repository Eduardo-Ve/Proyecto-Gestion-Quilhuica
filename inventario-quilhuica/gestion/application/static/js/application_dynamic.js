document.addEventListener("DOMContentLoaded", () => {
  const warehouseSelect = document.getElementById("id_ware");
  const formContainer = document.getElementById("formset-container");
  const addFormButton = document.getElementById("add-form");
  const totalFormsInput = document.querySelector("input[name$='TOTAL_FORMS']");
  const emptyFormTemplate = document.getElementById("empty-form-template");

  // 🔄 Cargar productos según caseta seleccionada
  async function loadProducts(warehouseId) {
    const selects = document.querySelectorAll("select[name$='product']");
    if (!warehouseId) {
      selects.forEach(s => (s.innerHTML = "<option value=''>Seleccione una caseta</option>"));
      return;
    }

    try {
      const res = await fetch(`/application/api/products/?warehouse_id=${warehouseId}`);
      const data = await res.json();

      if (!data.products) return;

      const options = data.products.map(
        (p) =>
          `<option value="${p.id}">${p.name} (${p.presentation}) — Stock: ${p.stock}</option>`
      );

      selects.forEach((select) => {
        const current = select.value;
        select.innerHTML = `<option value="">Seleccione un producto</option>${options.join("")}`;
        if (current && Array.from(select.options).some(o => o.value === current)) {
          select.value = current;
        }
      });

      updateAvailableProducts();
    } catch (err) {
      console.error("❌ Error al cargar productos:", err);
    }
  }

  // 🚫 Elimina completamente productos ya seleccionados
  function updateAvailableProducts() {
    const selects = document.querySelectorAll("select[name$='product']");
    const selectedValues = Array.from(selects)
      .map((s) => s.value)
      .filter((v) => v);

    selects.forEach((select) => {
      const current = select.value;
      const options = Array.from(select.options);

      options.forEach((opt) => {
        if (opt.value !== "" && selectedValues.includes(opt.value) && opt.value !== current) {
          opt.remove();
        }
      });
    });
  }

  // 🗑️ Eliminar fila de producto
  function addRemoveListeners() {
    document.querySelectorAll(".delete-btn").forEach((btn) => {
      btn.onclick = () => {
        const formDiv = btn.closest(".product-form");
        
        // ✅ Usar animación de fade out antes de eliminar
        formDiv.style.transition = "opacity 0.3s ease, transform 0.3s ease";
        formDiv.style.opacity = "0";
        formDiv.style.transform = "scale(0.95)";
        
        setTimeout(() => {
          formDiv.remove();
          updateFormCount();
          updateAvailableProducts();
        }, 300);
      };
    });
  }

  // ➕ Agregar nuevo producto
  addFormButton.addEventListener("click", () => {
    const formCount = parseInt(totalFormsInput.value);
    const templateHTML = emptyFormTemplate.innerHTML.replace(/__prefix__/g, formCount);

    const wrapper = document.createElement("div");
    wrapper.classList.add("product-form", "mb-3", "border", "p-3", "rounded");
    wrapper.innerHTML = templateHTML;

    // ✅ Animación de entrada
    wrapper.style.opacity = "0";
    wrapper.style.transform = "translateY(-10px)";
    
    formContainer.appendChild(wrapper);
    
    // Trigger animation
    setTimeout(() => {
      wrapper.style.transition = "opacity 0.3s ease, transform 0.3s ease";
      wrapper.style.opacity = "1";
      wrapper.style.transform = "translateY(0)";
    }, 10);
    
    updateFormCount();

    const warehouseId = warehouseSelect.value;
    if (warehouseId) loadProducts(warehouseId);

    addRemoveListeners();
  });

  // 🔢 Actualizar contador de formularios
  function updateFormCount() {
    const forms = document.querySelectorAll(".product-form");
    totalFormsInput.value = forms.length;
    
    // Actualizar los índices de cada formulario
    forms.forEach((form, index) => {
      const inputs = form.querySelectorAll("input, select");
      inputs.forEach(input => {
        if (input.name) {
          input.name = input.name.replace(/details-\d+-/, `details-${index}-`);
          input.id = input.id.replace(/id_details-\d+-/, `id_details-${index}-`);
        }
      });
    });
  }

  // 🧹 Resetear formulario si cambia la caseta
  warehouseSelect.addEventListener("change", () => {
    formContainer.innerHTML = "";
    totalFormsInput.value = 0;
    loadProducts(warehouseSelect.value);
  });

  // 🔁 Eventos generales
  document.addEventListener("change", (e) => {
    if (e.target.name && e.target.name.endsWith("product")) updateAvailableProducts();
  });

  // ✅ Validación antes de enviar el formulario
  const form = document.querySelector("form");
  if (form) {
    form.addEventListener("submit", (e) => {
      const productForms = document.querySelectorAll(".product-form");
      let hasValidProduct = false;

      productForms.forEach(productForm => {
        const productSelect = productForm.querySelector("select[name$='product']");
        const quantityInput = productForm.querySelector("input[name$='quantity_packages']");
        
        if (productSelect && productSelect.value && quantityInput && quantityInput.value) {
          hasValidProduct = true;
        }
      });

      if (!hasValidProduct) {
        e.preventDefault();
        alert("⚠️ Debes agregar al menos un producto con cantidad antes de guardar.");
        return false;
      }

      // Validar que todos los productos seleccionados tengan cantidad
      let isValid = true;
      productForms.forEach(productForm => {
        const productSelect = productForm.querySelector("select[name$='product']");
        const quantityInput = productForm.querySelector("input[name$='quantity_packages']");
        
        if (productSelect && productSelect.value && (!quantityInput || !quantityInput.value || quantityInput.value <= 0)) {
          isValid = false;
          quantityInput.style.border = "2px solid #dc3545";
          setTimeout(() => {
            quantityInput.style.border = "";
          }, 2000);
        }
        
        if (quantityInput && quantityInput.value && (!productSelect || !productSelect.value)) {
          isValid = false;
          productSelect.style.border = "2px solid #dc3545";
          setTimeout(() => {
            productSelect.style.border = "";
          }, 2000);
        }
      });

      if (!isValid) {
        e.preventDefault();
        alert("⚠️ Todos los productos deben tener una cantidad válida y viceversa.");
        return false;
      }
    });
  }

  // Inicialización
  if (warehouseSelect.value) loadProducts(warehouseSelect.value);
  addRemoveListeners();
});