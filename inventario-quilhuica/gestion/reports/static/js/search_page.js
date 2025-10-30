document.addEventListener("DOMContentLoaded", () => {
  console.log("✅ search_page.js cargado correctamente");

  const total = parseInt(document.querySelector(".pagination")?.dataset.total || "1");
  const ellipses = document.querySelectorAll(".jump-page");

  if (!ellipses.length) {
    console.warn("⚠️ No se encontraron botones '…'");
    return;
  }

  ellipses.forEach((el) => {
    el.addEventListener("click", (e) => {
      e.preventDefault();

      const container = el.parentElement.querySelector(".page-input");
      container.classList.toggle("d-none");

      const input = container.querySelector(".page-jump-input");
      input.focus();

      // Oculta al perder foco
      input.addEventListener("blur", () => container.classList.add("d-none"));

      // Detecta Enter
      input.addEventListener("keydown", (ev) => {
        if (ev.key === "Enter") {
          const page = parseInt(input.value);
          if (!isNaN(page) && page >= 1 && page <= total) {
            const params = new URLSearchParams(window.location.search);
            params.set("page", page);
            window.location.search = params.toString();
          } else {
            // ❌ Efecto visual si el número es inválido
            input.classList.add("input-error");

            // Reinicia la animación si se vuelve a intentar
            input.addEventListener("animationend", () => {
              input.classList.remove("input-error");
            }, { once: true });
          }
        }
      });
    });
  });
});
