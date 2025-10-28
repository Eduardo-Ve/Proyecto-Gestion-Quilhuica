document.addEventListener("DOMContentLoaded", () => {
  const chartData = JSON.parse(document.getElementById("chartData").textContent);

  // === GRÁFICOS ===
  // Top Stock
  new Chart(document.getElementById("chartStock"), {
    type: "bar",
    data: {
      labels: chartData.stock_labels,
      datasets: [{
        label: "Paquetes",
        data: chartData.stock_values,
        backgroundColor: "#3b82f6",
      }],
    },
    options: {
      responsive: true,
      scales: {
        x: { title: { display: true, text: "Producto" } },
        y: { title: { display: true, text: "Paquetes" } },
      },
    },
  });

  // Aplicaciones
  new Chart(document.getElementById("chartApps"), {
    type: "line",
    data: {
      labels: chartData.apps_labels,
      datasets: [{
        label: "Paquetes Aplicados",
        data: chartData.apps_values,
        borderColor: "#22c55e",
        tension: 0.3,
        fill: true,
        backgroundColor: "rgba(34,197,94,0.1)",
        pointRadius: 4,
      }],
    },
    options: {
      responsive: true,
      scales: {
        x: { title: { display: true, text: "Fecha" } },
        y: { title: { display: true, text: "Cantidad" } },
      },
    },
  });

  // Traslados
  new Chart(document.getElementById("chartMoves"), {
    type: "line",
    data: {
      labels: chartData.moves_labels,
      datasets: [{
        label: "Cantidad Trasladada",
        data: chartData.moves_values,
        borderColor: "#6366f1",
        tension: 0.3,
        fill: true,
        backgroundColor: "rgba(99,102,241,0.1)",
        pointRadius: 4,
      }],
    },
    options: {
      responsive: true,
      scales: {
        x: { title: { display: true, text: "Fecha" } },
        y: { title: { display: true, text: "Cantidad" } },
      },
    },
  });

  // Stock por Categoría
  new Chart(document.getElementById("chartCat"), {
    type: "doughnut",
    data: {
      labels: chartData.cat_labels,
      datasets: [{
        label: "Stock",
        data: chartData.cat_values,
        backgroundColor: [
          "#3b82f6", "#22c55e", "#6366f1", "#f59e0b", "#ef4444"
        ],
      }],
    },
    options: {
      responsive: true,
      aspect_ratio: 2,
      plugins: {
        legend: { position: "bottom" },
      },
    },
  });

  // === ANIMACIÓN DE TABLA NOTIFICACIONES ===
  const unreadRows = document.querySelectorAll(".notification-row.unread");
  unreadRows.forEach((row) => {
    row.addEventListener("click", () => {
      row.classList.add("read-transition");
      setTimeout(() => {
        row.classList.remove("unread", "read-transition");
      }, 1500);
    });
  });

  // === ANIMACIÓN DE ENTRADA DE GRÁFICOS ===
  document.querySelectorAll(".chart-card").forEach((card, i) => {
    card.style.opacity = 0;
    setTimeout(() => {
      card.style.transition = "opacity 0.6s ease";
      card.style.opacity = 1;
    }, 150 * i);
  });

  // === 🧾 Tooltip de mensaje al hacer clic en el producto ===
  document.querySelectorAll(".product-cell").forEach((cell) => {
    // 1) Tomamos el valor crudo del data-attribute
    const raw = cell.dataset.message || "";

    // 2) Lo decodificamos (convierte \uXXXX, \n, \" , etc.)
    let message = raw;
    try {
      message = JSON.parse(`"${raw}"`);
    } catch (e) {
      // si algo raro pasa, usamos el crudo
      message = raw;
    }

    // 3) Si quieres respetar saltos de línea, conviértelos a <br>
    const htmlMessage = message.replace(/\n/g, "<br>");

    // 4) Construimos el tooltip
    const tooltip = document.createElement("div");
    tooltip.className = "product-tooltip";
    tooltip.innerHTML = htmlMessage;
    cell.appendChild(tooltip);

    cell.addEventListener("click", (e) => {
      e.stopPropagation();
      const visible = tooltip.style.display === "block";
      document.querySelectorAll(".product-tooltip").forEach((t) => (t.style.display = "none"));
      tooltip.style.display = visible ? "none" : "block";
    });
  });

  document.addEventListener("click", () => {
    document.querySelectorAll(".product-tooltip").forEach((t) => (t.style.display = "none"));
  });

  // === AJAX PARA ACTUALIZAR "ACTIVIDAD RECIENTE" CADA 5 MINUTOS ===
  const FEED_URL = "/dashboard/activity-feed/";  // Ajustar si tu URL es distinta
  const feedEl = document.getElementById("activity-feed");
  const statusEl = document.getElementById("activity-status");

  async function updateActivityFeed() {
    try {
      if (statusEl) statusEl.textContent = "Actualizando…";

      const resp = await fetch(FEED_URL, { cache: "no-store" });
      const data = await resp.json();

      // Si no vienen datos → mensaje vacío
      if (!data.items || data.items.length === 0) {
        feedEl.innerHTML = `
          <li class="list-group-item text-muted small py-3 text-center">
            No hay actividad reciente registrada.
          </li>`;
        if (statusEl) statusEl.textContent = "Sin actividad";
        return;
      }

      // Renderizar lista con animación
      feedEl.classList.remove("show");
      feedEl.innerHTML = data.items.map(it => `
        <li class="list-group-item d-flex flex-column border-0 border-bottom small py-2">
          <div class="d-flex justify-content-between align-items-center">
            <span>
              <i class="bi bi-${it.icon} me-1"></i>
              ${it.title}
            </span>
            <small class="text-muted">${it.when}</small>
          </div>
          <span class="text-muted ms-4">
            <i class="bi bi-person-circle me-1"></i>${it.by}
          </span>
        </li>
      `).join("");

      // Activar fade-in suave
      setTimeout(() => feedEl.classList.add("show"), 50);

      if (statusEl) statusEl.textContent = "Actualizado";
    } catch (error) {
      if (statusEl) statusEl.textContent = "Sin conexión";
    }
  }

  // Ejecutar ahora
  updateActivityFeed();

  // Ejecutar automáticamente cada 5 minutos (300000 ms)
  setInterval(updateActivityFeed, 300000);

});