document.addEventListener("DOMContentLoaded", () => {
  const fp = flatpickr("#id_expire_at", {
    appendTo: document.body,
    dateFormat: "Y-m-d",
    altInput: true,
    altFormat: "d \\d\\e F \\d\\e Y",
    allowInput: false,
    disableMobile: true,
    minDate: "today",

    locale: {
      firstDayOfWeek: 1,
      weekdays: {
        shorthand: ["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sa"],
        longhand: [
          "Domingo",
          "Lunes",
          "Martes",
          "Miércoles",
          "Jueves",
          "Viernes",
          "Sábado",
        ],
      },
      months: {
        shorthand: [
          "Ene", "Feb", "Mar", "Abr", "May", "Jun",
          "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
        ],
        longhand: [
          "Enero", "Febrero", "Marzo", "Abril", "Mayo",
          "Junio", "Julio", "Agosto", "Septiembre",
          "Octubre", "Noviembre", "Diciembre",
        ],
      },
    },

    onReady: function (selectedDates, dateStr, instance) {
      const container = instance.calendarContainer;
      if (!container) return;

      // 🎨 Paleta institucional
      container.style.setProperty("--fp-primary", "#00C451");
      container.style.setProperty("--fp-primary-hover", "#055526");
      container.style.setProperty("--fp-text", "#1E1E1E");

      // === OBTENER FLECHAS NATIVAS DE FLATPICKR ===
      const prevArrow = container.querySelector(".flatpickr-prev-month");
      const nextArrow = container.querySelector(".flatpickr-next-month");

      // === CABECERA PERSONALIZADA ===
      const header = container.querySelector(".flatpickr-current-month");
      if (!header) return;

      // Limpiar el contenido pero mantener las flechas
      const monthElement = header.querySelector(".flatpickr-monthDropdown-months");
      const yearElement = header.querySelector(".numInputWrapper");
      if (monthElement) monthElement.remove();
      if (yearElement) yearElement.remove();

      // Crear título personalizado
      const title = document.createElement("div");
      title.classList.add("fp-title-custom");
      title.style.cursor = "pointer";
      title.style.fontWeight = "600";
      title.style.fontSize = "1rem";
      title.style.color = "#fff";
      title.style.flex = "1";
      title.style.textAlign = "center";
      title.style.padding = "0 10px";

      header.appendChild(title);

      // Asegurar que las flechas sean visibles y estén estilizadas
      if (prevArrow) {
        prevArrow.style.display = "flex";
        prevArrow.style.color = "#fff";
      }
      if (nextArrow) {
        nextArrow.style.display = "flex";
        nextArrow.style.color = "#fff";
      }

      // === VISTAS ===
      let view = "days";
      let currentDecadeStart = instance.currentYear - (instance.currentYear % 12);

      function renderDays() {
        view = "days";
        removeCustomGrid();
        const daysContainer = container.querySelector(".flatpickr-days");
        const weekDays = container.querySelector(".flatpickr-weekdays");
        if (daysContainer) daysContainer.style.display = "";
        if (weekDays) weekDays.style.display = "";
        title.textContent = `${instance.l10n.months.longhand[instance.currentMonth]} ${instance.currentYear}`;
        
        // Restaurar comportamiento normal de las flechas
        if (prevArrow) prevArrow.onclick = null;
        if (nextArrow) nextArrow.onclick = null;
      }

      function renderMonths() {
        view = "months";
        const grid = document.createElement("div");
        grid.classList.add("fp-months-grid");

        instance.l10n.months.longhand.forEach((m, i) => {
          const btn = document.createElement("div");
          btn.classList.add("fp-month-btn");
          btn.textContent = m;
          btn.onclick = () => {
            instance.changeMonth(i - instance.currentMonth);
            renderDays();
          };
          grid.appendChild(btn);
        });

        setCustomGrid(grid, `${instance.currentYear}`);
        
        // Ocultar flechas en vista de meses
        if (prevArrow) prevArrow.style.visibility = "hidden";
        if (nextArrow) nextArrow.style.visibility = "hidden";
      }

      function renderYears(startYear = currentDecadeStart) {
        view = "years";
        currentDecadeStart = startYear;
        const grid = document.createElement("div");
        grid.classList.add("fp-years-grid");

        for (let y = startYear; y < startYear + 12; y++) {
          const btn = document.createElement("div");
          btn.classList.add("fp-year-btn");
          btn.textContent = y;
          btn.onclick = () => {
            instance.changeYear(y);
            renderMonths();
          };
          grid.appendChild(btn);
        }

        setCustomGrid(grid, `${startYear} - ${startYear + 11}`);
        
        // Mostrar flechas y usar para cambiar década
        if (prevArrow) {
          prevArrow.style.visibility = "visible";
          prevArrow.onclick = (e) => {
            e.preventDefault();
            e.stopPropagation();
            renderYears(startYear - 12);
          };
        }
        if (nextArrow) {
          nextArrow.style.visibility = "visible";
          nextArrow.onclick = (e) => {
            e.preventDefault();
            e.stopPropagation();
            renderYears(startYear + 12);
          };
        }
      }

      // === CONTENEDOR DE GRILLAS ===
      function setCustomGrid(grid, titleText) {
        removeCustomGrid();
        const daysContainer = container.querySelector(".flatpickr-days");
        const weekDays = container.querySelector(".flatpickr-weekdays");
        if (daysContainer) daysContainer.style.display = "none";
        if (weekDays) weekDays.style.display = "none";

        const wrapper = document.createElement("div");
        wrapper.classList.add("fp-grid-container");
        wrapper.appendChild(grid);
        container.querySelector(".flatpickr-innerContainer").appendChild(wrapper);

        // ✅ Actualiza el título del header verde
        title.textContent = titleText;
      }

      // === LIMPIAR ===
      function removeCustomGrid() {
        const existing = container.querySelector(".fp-grid-container");
        if (existing) existing.remove();
      }

      // === EVENTOS ===
      title.addEventListener("click", () => {
        if (view === "days") renderMonths();
        else if (view === "months") renderYears();
        else renderDays();
      });

      instance._input.addEventListener("focus", () => {
        removeCustomGrid();
        renderDays();
      });

      renderDays();
    },
  });
});