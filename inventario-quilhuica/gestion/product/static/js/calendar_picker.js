document.addEventListener("DOMContentLoaded", () => {
  // Selecciona todos los inputs tipo date del proyecto
  const dateInputs = document.querySelectorAll("input[type='date'], .dateinput");

  dateInputs.forEach((input) => {
    flatpickr(input, {
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
        container.style.setProperty("--fp-primary", "#00C451");
        container.style.setProperty("--fp-primary-hover", "#055526");
        container.style.setProperty("--fp-text", "#1E1E1E");
      },
    });
  });
});
