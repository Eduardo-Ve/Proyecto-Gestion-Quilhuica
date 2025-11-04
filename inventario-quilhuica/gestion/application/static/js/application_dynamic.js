document.addEventListener("DOMContentLoaded", () => {
  const warehouseSelect = document.getElementById("id_ware");
  const formContainer = document.getElementById("formset-container");
  const addFormButton = document.getElementById("add-form");
  const totalFormsInput = document.querySelector("input[name$='TOTAL_FORMS']");
  const emptyFormTemplate = document.getElementById("empty-form-template");

  if (!formContainer || !addFormButton || !emptyFormTemplate || !totalFormsInput) {
    console.warn("⚠️ Elementos del formset no encontrados. Verifica IDs en HTML.");
    return;
  }

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
        p => `<option value="${p.id}">${p.name} (${p.presentation}) — Stock: ${p.stock}</option>`
      );

      selects.forEach(select => {
        const current = select.value;
        select.innerHTML = `<option value="">Seleccione un producto</option>${options.join("")}`;
        if (current && Array.from(select.options).some(o => o.value === current)) {
          select.value = current;
        }
      });

      updateAvailableProducts();
    } catch (err) {
      console.error("Error al cargar productos:", err);
    }
  }

  function updateAvailableProducts() {
    const selects = document.querySelectorAll("select[name$='product']");
    const selectedValues = Array.from(selects)
      .map(s => s.value)
      .filter(v => v);

    selects.forEach(select => {
      const current = select.value;
      Array.from(select.options).forEach(opt => {
        if (opt.value !== "" && selectedValues.includes(opt.value) && opt.value !== current) {
          opt.disabled = true;
        } else {
          opt.disabled = false;
        }
      });
    });
  }

  function addRemoveListeners() {
    document.querySelectorAll(".delete-btn").forEach(btn => {
      btn.onclick = () => {
        const formDiv = btn.closest(".product-form");
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

  addFormButton.addEventListener("click", () => {
    const formCount = parseInt(totalFormsInput.value);
    const templateHTML = emptyFormTemplate.innerHTML.replace(/__prefix__/g, formCount);

    const wrapper = document.createElement("div");
    wrapper.classList.add("product-form", "mb-3", "border", "p-3", "rounded");
    wrapper.innerHTML = templateHTML;

    wrapper.style.opacity = "0";
    wrapper.style.transform = "translateY(-10px)";
    formContainer.appendChild(wrapper);

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

  function updateFormCount() {
    const forms = document.querySelectorAll(".product-form");
    totalFormsInput.value = forms.length;
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

  warehouseSelect.addEventListener("change", () => {
    formContainer.innerHTML = "";
    totalFormsInput.value = 0;
    loadProducts(warehouseSelect.value);
  });

  document.addEventListener("change", e => {
    if (e.target.name && e.target.name.endsWith("product")) updateAvailableProducts();
  });

  // inicialización
  if (warehouseSelect.value) loadProducts(warehouseSelect.value);
  addRemoveListeners();
});
