// Mostrar/ocultar “Nueva categoría”
const chk = document.getElementById("id_create_new_category");
const newCat = document.getElementById("new-cat");
const existingCat = document.getElementById("id_category")?.closest(".col-md-6");

function toggleCat() {
  const isChecked = chk && chk.checked;

  // Mostrar u ocultar campos según estado del checkbox
  if (newCat) newCat.style.display = isChecked ? "" : "none";
  if (existingCat) existingCat.style.display = isChecked ? "none" : "";
}

if (chk) {
  chk.addEventListener("change", toggleCat);
  toggleCat(); // inicializar al cargar
}

// Utilidad: reemplaza __prefix__ por índice
function replacePrefix(html, index) {
  return html.replaceAll(/__prefix__/g, String(index));
}

// Añadir fila al formset usando empty_form
const addBtn = document.getElementById("add-row");
const rows = document.getElementById("formset-rows");
const tmpl = document.getElementById("empty-form-template");
const totalInput = document.getElementById("id_form-TOTAL_FORMS");

function addEmptyRow() {
  const index = parseInt(totalInput.value || "0", 10);
  const html = replacePrefix(tmpl.innerHTML, index);
  const wrapper = document.createElement("div");
  wrapper.innerHTML = html.trim();
  rows.appendChild(wrapper.firstElementChild);
  totalInput.value = index + 1;
}

addBtn?.addEventListener("click", addEmptyRow);

// Si no hay filas renderizadas (extra=0 y sin instancias), creamos 1 al cargar
document.addEventListener("DOMContentLoaded", () => {
  if (!rows.querySelector(".col-12.border")) {
    addEmptyRow();
  }
});
