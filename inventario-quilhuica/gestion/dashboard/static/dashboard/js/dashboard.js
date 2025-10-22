(function () {
  const D = window.DASH_DATA || {};
  console.log("📊 DASH_DATA recibido:", D);

  function safeArray(x) {
    return Array.isArray(x) ? x : [];
  }

  const charts = {
    movimientos: document.getElementById("chart-movimientos"),
    stock: document.getElementById("chart-stock-shed"),
    top: document.getElementById("chart-top-used"),
    cat: document.getElementById("chart-used-cat"),
  };

  // 1️⃣ Movimientos por día
  const movData = safeArray(D.chart_mov_daily);
  if (charts.movimientos && movData.length) {
    const grouped = {};
    movData.forEach(r => {
      if (!grouped[r.movement_type]) grouped[r.movement_type] = [];
      grouped[r.movement_type].push(r);
    });
    const traces = Object.entries(grouped).map(([type, arr]) => ({
      x: arr.map(a => a.day),
      y: arr.map(a => a.total),
      name: type,
      type: 'bar'
    }));
    Plotly.newPlot(charts.movimientos, traces, {
      barmode: 'stack',
      xaxis: { title: 'Fecha' },
      yaxis: { title: 'Cantidad movida' },
      margin: { t: 30, r: 10, l: 40, b: 40 },
    }, { responsive: true });
  } else if (charts.movimientos) {
    charts.movimientos.innerHTML = "<div class='text-muted text-center p-3'>Sin datos de movimientos</div>";
  }

  // 2️⃣ Stock por caseta
  const stockData = safeArray(D.chart_stock_by_shed);
  if (charts.stock && stockData.length) {
    const labels = stockData.map(x => x["warehouse__name_ware"]);
    const values = stockData.map(x => x.total);
    Plotly.newPlot(charts.stock, [{ labels, values, type: 'pie', hole: .35 }], {
      legend: { orientation: 'h' },
      margin: { t: 30, r: 10, l: 10, b: 10 },
    }, { responsive: true });
  } else if (charts.stock) {
    charts.stock.innerHTML = "<div class='text-muted text-center p-3'>Sin datos de stock</div>";
  }

  // 3️⃣ Top productos
  const topData = safeArray(D.chart_top_used);
  if (charts.top && topData.length) {
    const x = topData.map(x => x["product__name_prod"]).reverse();
    const y = topData.map(x => x.total).reverse();
    Plotly.newPlot(charts.top, [{
      x: y, y: x, type: 'bar', orientation: 'h'
    }], {
      margin: { t: 30, r: 20, l: 150, b: 40 },
      xaxis: { title: 'Cantidad usada' },
      yaxis: { automargin: true },
    }, { responsive: true });
  } else if (charts.top) {
    charts.top.innerHTML = "<div class='text-muted text-center p-3'>Sin datos de productos</div>";
  }

  // 4️⃣ Consumo por categoría
  const catData = safeArray(D.chart_used_by_cat);
  if (charts.cat && catData.length) {
    const x = catData.map(x => x["product__category__name_cat"]);
    const y = catData.map(x => x.total);
    Plotly.newPlot(charts.cat, [{
      x, y, type: 'scatter', mode: 'lines+markers'
    }], {
      xaxis: { title: 'Categoría' },
      yaxis: { title: 'Cantidad usada' },
      margin: { t: 30, r: 20, l: 40, b: 40 },
    }, { responsive: true });
  } else if (charts.cat) {
    charts.cat.innerHTML = "<div class='text-muted text-center p-3'>Sin datos de consumo</div>";
  }
})();