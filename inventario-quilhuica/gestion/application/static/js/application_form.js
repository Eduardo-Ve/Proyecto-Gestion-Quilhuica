document.addEventListener("DOMContentLoaded", () => {
  const casetaSelect = document.getElementById("id_ware");
  const sectorSelect = document.getElementById("id_sector");

  // 🔹 Recuperar atributos de usuario desde el HTML
  const userIsStaff = casetaSelect?.dataset.userIsStaff === "true";
  const casetaAsignadaId = casetaSelect?.dataset.casetaAsignadaId || null;

  async function loadSectores(casetaId) {
    if (!casetaId) {
      sectorSelect.innerHTML = '<option value="">Seleccione una caseta</option>';
      return;
    }

    try {
      const response = await fetch(`/application/ajax/sectores_by_caseta/?caseta_id=${casetaId}`);
      const data = await response.json();

      sectorSelect.innerHTML = '<option value="">Seleccione un sector</option>';
      data.forEach(grupo => {
        const optgroup = document.createElement("optgroup");
        optgroup.label = grupo.equipo;
        grupo.sectores.forEach(s => {
          const option = document.createElement("option");
          option.value = s.id;
          option.textContent = s.nombre;
          optgroup.appendChild(option);
        });
        sectorSelect.appendChild(optgroup);
      });
    } catch (err) {
      console.error("❌ Error al cargar sectores:", err);
      sectorSelect.innerHTML = '<option value="">Error al cargar sectores</option>';
    }
  }

  // 🔹 Admin: carga sectores al cambiar caseta
  casetaSelect?.addEventListener("change", function () {
    loadSectores(this.value);
  });

  // 🔹 Encargado: carga automática al entrar
  if (!userIsStaff && casetaAsignadaId) {
    loadSectores(casetaAsignadaId);
  }
});
