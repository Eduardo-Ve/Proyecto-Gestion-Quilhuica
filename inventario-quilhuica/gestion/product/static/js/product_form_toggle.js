document.addEventListener("DOMContentLoaded", () => {
  const chkNewCat = document.getElementById("id_create_new_category");
  const selCategory = document.getElementById("id_category");
  const newCatBlock = document.getElementById("new-cat");

  const chkNewPres = document.getElementById("id_create_new_presentation");
  const selPres = document.getElementById("id_presentation");
  const newPresBlock = document.getElementById("new-presentation");

  function toggle(el, state) {
    if (!el) return;
    el.classList.toggle("is-hidden", !state);
    el.querySelectorAll("input, select, textarea").forEach(input => {
      input.disabled = !state;
    });
  }

  function handleCategory() {
    if (!chkNewCat) return;
    toggle(newCatBlock, chkNewCat.checked);
    if (selCategory) selCategory.disabled = chkNewCat.checked;
    document.getElementById("category-select-wrapper").classList.toggle("is-hidden", chkNewCat.checked);
  }

  function handlePresentation() {
    if (!chkNewPres) return;
    toggle(newPresBlock, chkNewPres.checked);
    if (selPres) selPres.disabled = chkNewPres.checked;
    document.getElementById("presentation-select-wrapper").classList.toggle("is-hidden", chkNewPres.checked);
  }

  handleCategory();
  handlePresentation();

  if (chkNewCat) chkNewCat.addEventListener("change", handleCategory);
  if (chkNewPres) chkNewPres.addEventListener("change", handlePresentation);
});

