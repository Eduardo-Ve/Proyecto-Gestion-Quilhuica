document.addEventListener("DOMContentLoaded", () => {
  const fp = flatpickr("#id_expire_at", {
    appendTo: document.body, // ✅ fuerza a renderizar dentro del body
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

      // 🎨 Paleta institucional
      container.style.setProperty("--fp-primary", "#00C451");
      container.style.setProperty("--fp-primary-hover", "#055526");
      container.style.setProperty("--fp-text", "#1E1E1E");

      // Cabecera personalizada
      const header = container.querySelector(".flatpickr-current-month");
      if (!header) return;

      const title = document.createElement("div");
      title.classList.add("fp-title-custom");
      title.style.cursor = "pointer";
      title.style.fontWeight = "600";
      title.style.fontSize = "1rem";
      title.style.color = "#fff";

      header.innerHTML = "";
      header.appendChild(title);

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

        setCustomGrid(grid, `${startYear} - ${startYear + 11}`, {
          prev: () => renderYears(startYear - 12),
          next: () => renderYears(startYear + 12),
        });
      }

      function setCustomGrid(grid, titleText, nav = null) {
        removeCustomGrid();

        const daysContainer = container.querySelector(".flatpickr-days");
        const weekDays = container.querySelector(".flatpickr-weekdays");
        if (daysContainer) daysContainer.style.display = "none";
        if (weekDays) weekDays.style.display = "none";

        const wrapper = document.createElement("div");
        wrapper.classList.add("fp-grid-container");

        if (nav) {
          const navWrapper = document.createElement("div");
          navWrapper.classList.add("fp-nav-decade");

          const prev = document.createElement("span");
          prev.classList.add("fp-decade-arrow");
          prev.innerHTML = "&#171;";
          prev.onclick = nav.prev;

          const next = document.createElement("span");
          next.classList.add("fp-decade-arrow");
          next.innerHTML = "&#187;";
          next.onclick = nav.next;

          const label = document.createElement("span");
          label.classList.add("fp-decade-label");
          label.textContent = titleText;

          navWrapper.append(prev, label, next);
          wrapper.appendChild(navWrapper);
        }

        wrapper.appendChild(grid);
        container.querySelector(".flatpickr-innerContainer").appendChild(wrapper);
        title.textContent = titleText;
      }

      function removeCustomGrid() {
        const existing = container.querySelector(".fp-grid-container");
        if (existing) existing.remove();
      }

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
