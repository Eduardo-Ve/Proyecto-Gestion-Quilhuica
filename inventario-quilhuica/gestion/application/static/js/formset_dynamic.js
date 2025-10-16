document.addEventListener("DOMContentLoaded", function () {
  const addButton = document.getElementById("add-row");
  const formsetBody = document.getElementById("formset-body");
  const totalForms = document.querySelector("#id_details-TOTAL_FORMS");

  // Mapea producto -> presentación desde opciones del select
  function getPresentationFromProduct(selectEl) {
    const selectedOption = selectEl.options[selectEl.selectedIndex];
    return selectedOption.dataset.presentation || "";
  }

  // Actualiza presentación cuando cambia el producto
  formsetBody.addEventListener("change", function (e) {
    if (e.target.classList.contains("product-select")) {
      const row = e.target.closest(".form-row");
      const presField = row.querySelector(".presentation-field");
      presField.value = getPresentationFromProduct(e.target);
    }
  });

  addButton.addEventListener("click", function () {
    const formRows = formsetBody.querySelectorAll(".form-row");
    const newForm = formRows[formRows.length - 1].cloneNode(true);
    const formRegex = new RegExp(`details-(\\d+)-`, "g");
    const formCount = formRows.length;

    newForm.innerHTML = newForm.innerHTML.replace(formRegex, `details-${formCount}-`);
    formsetBody.appendChild(newForm);
    totalForms.value = formRows.length + 1;

    // Limpia valores
    newForm.querySelectorAll("input, select").forEach((input) => {
      if (input.type !== "hidden") input.value = "";
    });
  });

  formsetBody.addEventListener("click", function (e) {
    if (e.target.classList.contains("remove-row")) {
      const formRows = formsetBody.querySelectorAll(".form-row");
      if (formRows.length > 1) {
        e.target.closest(".form-row").remove();
        totalForms.value = formRows.length - 1;
      } else {
        alert("Debe haber al menos una fila.");
      }
    }
  });
});
