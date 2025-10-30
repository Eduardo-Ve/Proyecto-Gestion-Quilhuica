// === CONTROL DE CATEGORÍA ===
const chkCat = document.getElementById("id_create_new_category");
const newCat = document.getElementById("new-cat");
const existingCat = document.getElementById("id_category")?.closest(".col-md-6");

function toggleCategory() {
  const isChecked = chkCat && chkCat.checked;
  if (newCat) newCat.style.display = isChecked ? "" : "none";
  if (existingCat) existingCat.style.display = isChecked ? "none" : "";
}

if (chkCat) {
  chkCat.addEventListener("change", toggleCategory);
  toggleCategory(); // aplicar al cargar
}

// === CONTROL DE PRESENTACIÓN ===
const chkPres = document.getElementById("id_create_new_presentation");
const newPres = document.getElementById("new-pres");
const existingPres = document.getElementById("id_presentation")?.closest(".col-md-6");

function togglePresentation() {
  const isChecked = chkPres && chkPres.checked;
  if (newPres) newPres.style.display = isChecked ? "" : "none";
  if (existingPres) existingPres.style.display = isChecked ? "none" : "";
}

if (chkPres) {
  chkPres.addEventListener("change", togglePresentation);
  togglePresentation();
}

// === UTILIDAD FORMSET (si se usa con presentaciones dinámicas) ===
function replacePrefix(html, index) {
  return html.replaceAll(/__prefix__/g, String(index));
}

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

document.addEventListener("DOMContentLoaded", () => {
  if (rows && !rows.querySelector(".col-12.border")) {
    addEmptyRow();
  }
});

