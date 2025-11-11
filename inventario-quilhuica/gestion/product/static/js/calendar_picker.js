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
          "Domingo", "Lunes", "Martes", "Miércoles",
          "Jueves", "Viernes", "Sábado",
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

      // === Obtener flechas ===
      const prevArrow = container.querySelector(".flatpickr-prev-month");
      const nextArrow = container.querySelector(".flatpickr-next-month");

      // === Cabecera personalizada ===
      const header = container.querySelector(".flatpickr-current-month");
      if (!header) return;

      // Eliminar contenido original del mes/año
      const monthElement = header.querySelector(".flatpickr-monthDropdown-months");
      const yearElement = header.querySelector(".numInputWrapper");
      if (monthElement) monthElement.remove();
      if (yearElement) yearElement.remove();

      // Crear nuevo título
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

      // Estilo flechas
      if (prevArrow) {
        prevArrow.style.display = "flex";
        prevArrow.style.color = "#fff";
      }
      if (nextArrow) {
        nextArrow.style.display = "flex";
        nextArrow.style.color = "#fff";
      }

      // === Vistas personalizadas ===
      let view = "days";
      let currentDecadeStart = instance.currentYear - (instance.currentYear % 12);

      function updateTitle() {
        title.textContent = `${instance.l10n.months.longhand[instance.currentMonth]} ${instance.currentYear}`;
      }

      function renderDays() {
        view = "days";
        removeCustomGrid();
        const daysContainer = container.querySelector(".flatpickr-days");
        const weekDays = container.querySelector(".flatpickr-weekdays");
        if (daysContainer) daysContainer.style.display = "";
        if (weekDays) weekDays.style.display = "";
        updateTitle();

        // Restaurar comportamiento normal de flechas
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

        // Ocultar flechas
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

        // Mostrar flechas y usarlas para cambiar década
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

      // === Contenedor para grid custom ===
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

        title.textContent = titleText;
      }

      function removeCustomGrid() {
        const existing = container.querySelector(".fp-grid-container");
        if (existing) existing.remove();
      }

      // === Eventos ===
      title.addEventListener("click", () => {
        if (view === "days") renderMonths();
        else if (view === "months") renderYears();
        else renderDays();
      });

      instance._input.addEventListener("focus", () => {
        removeCustomGrid();
        renderDays();
      });

      // Hooks para actualizar título al cambiar mes o año
      instance.config.onMonthChange.push(updateTitle);
      instance.config.onYearChange.push(updateTitle);

      // Render inicial
      renderDays();
    },
  });
});
