(function () {
  const $ = (id) => document.getElementById(id);
  const TABS = [
    ["salud", "SALUD"],
    ["finanzas", "FINANZAS"],
    ["ejercicio", "EJERCICIO"],
    ["comida", "DIETA"],
    ["cals", "CALENDARIOS"],
    ["inbox", "MENSAJES"],
  ];

  const views = {
    salud() {
      return `
      <div class="dash-grid">
        <section class="card w4"><span class="kicker">Hoy</span><div class="metric">7.2<small>HORAS DE SUEÑO</small></div><div class="bar"><i style="width:80%"></i></div></section>
        <section class="card w4"><span class="kicker">Recuperación</span><div class="metric">82<small>SCORE</small></div><div class="bar"><i style="width:82%"></i></div></section>
        <section class="card w4"><span class="kicker">Pasos</span><div class="metric">4 120<small>META 8 000</small></div><div class="bar"><i style="width:51%"></i></div></section>
        <section class="card w8">
          <span class="kicker">Cuerpo</span><h2>Salud general</h2>
          <div class="row"><span>FC reposo</span><span>61 bpm</span></div>
          <div class="row"><span>HRV</span><span>48 ms</span></div>
          <div class="row"><span>Peso</span><span>pendiente de báscula</span></div>
          <div class="row"><span>Ánimo</span><span class="ok">estable</span></div>
        </section>
        <section class="card w4">
          <span class="kicker">Alertas</span><h2>LOONA vigila</h2>
          <p class="pill">CONECTAR Apple Salud / Withings</p>
          <div class="row"><span>Hidratación</span><span>2 / 3 L</span></div>
          <div class="row"><span>Suplementos</span><span>mañana pendiente</span></div>
        </section>
      </div>`;
    },
    finanzas() {
      return `
      <div class="dash-grid">
        <section class="card w4"><span class="kicker">Ingresos mes</span><div class="metric">$48.2k<small>MXN · AGOSTO</small></div></section>
        <section class="card w4"><span class="kicker">Gastos</span><div class="metric">$31.7k<small>62% DEL MES</small></div></section>
        <section class="card w4"><span class="kicker">Libre</span><div class="metric">$16.5k<small>DESPUÉS DE FIJOS</small></div></section>
        <section class="card w6">
          <span class="kicker">Suscripciones</span><h2>Se cobran solas</h2>
          <div class="row"><span>iCloud+</span><span>$99</span></div>
          <div class="row"><span>SuperGrok</span><span>activa</span></div>
          <div class="row"><span>Gemini Workspace</span><span>Enterprise</span></div>
          <div class="row"><span>Publora</span><span>activa</span></div>
        </section>
        <section class="card w6">
          <span class="kicker">Deudas · tarjetas · servicios</span><h2>Compromisos</h2>
          <div class="row"><span>Tarjeta 1</span><span class="bad">corte 18</span></div>
          <div class="row"><span>CFE / agua / internet</span><span>3 servicios</span></div>
          <div class="row"><span>Renta / predial</span><span>anotar</span></div>
          <p class="pill" style="margin-top:10px">CONECTAR CSV / Notion Finanzas — no inventar saldos</p>
        </section>
      </div>`;
    },
    ejercicio() {
      return `
      <div class="dash-grid">
        <section class="card w6">
          <span class="kicker">Hoy · miércoles</span><h2>Core y postura</h2>
          <div class="row"><span>Dead bug</span><span>3 × 10</span></div>
          <div class="row"><span>Bird dog</span><span>3 × 8</span></div>
          <div class="row"><span>Plancha lateral</span><span>40 s</span></div>
          <div class="bar"><i style="width:0%"></i></div>
        </section>
        <section class="card w6">
          <span class="kicker">Racha</span><div class="metric">0<small>DÍAS REGISTRADOS</small></div>
          <div class="row"><span>Meta semanal</span><span>5 sesiones</span></div>
          <div class="row"><span>Motivación</span><span>mañana ya te lo dijo LOONA</span></div>
        </section>
      </div>`;
    },
    comida() {
      return `
      <div class="dash-grid">
        <section class="card w12">
          <span class="kicker">Alimentación</span><h2>Dieta del día</h2>
          <div class="row"><span>Desayuno</span><span>proteína + fruta · anotar</span></div>
          <div class="row"><span>Comida</span><span>—</span></div>
          <div class="row"><span>Cena</span><span>—</span></div>
          <div class="row"><span>Agua</span><span>2 / 3 L</span></div>
          <p class="pill" style="margin-top:10px">Corto plazo: captura rápida por voz. “LOONA, desayuné huevos.”</p>
        </section>
      </div>`;
    },
    cals() {
      return `
      <div class="dash-grid">
        <section class="card w6"><span class="kicker">Actividades</span><h2>Vida</h2><div class="row"><span>Hoy</span><span>core 10 min</span></div><div class="row"><span>Vie</span><span>Farmasi catálogo</span></div></section>
        <section class="card w6"><span class="kicker">Redes</span><h2>Publicaciones</h2><div class="row"><span>Likinya</span><span>Stories + feed</span></div><div class="row"><span>LOONA</span><span>explainer pendiente créditos</span></div></section>
        <section class="card w6"><span class="kicker">Trabajo</span><h2>Studio</h2><div class="row"><span>P1 Likinya</span><span>publish live</span></div><div class="row"><span>P2 LOONA</span><span>HUD + dashboards</span></div></section>
        <section class="card w6"><span class="kicker">Proyectos</span><h2>Tablero</h2><div class="row"><span>AMDA</span><span>ver vault</span></div><div class="row"><span>Gutierrez Consulting</span><span>ver vault</span></div></section>
      </div>`;
    },
    inbox() {
      return `
      <div class="dash-grid">
        <section class="card w12">
          <span class="kicker">Centro de mensajes</span><h2>Una bandeja. Tú la ordenas.</h2>
          <div class="msg"><b>GMAIL</b><span>sin sync todavía</span><span>conectar</span></div>
          <div class="msg"><b>WHATSAPP</b><span>API business / puente local</span><span>NEED_HUMAN</span></div>
          <div class="msg"><b>IG</b><span>DMs no salen por Publora</span><span>browser</span></div>
          <div class="msg"><b>FB MSN</b><span>igual que IG</span><span>browser</span></div>
          <div class="msg"><b>TIKTOK</b><span>inbox nativo</span><span>browser</span></div>
          <div class="msg"><b>TELEGRAM</b><span>LOONA bot</span><span>falta token</span></div>
          <p class="pill" style="margin-top:12px">Regla: un canal = un conector. Arrastrar columnas cuando haya datos reales. Cero mensajes inventados.</p>
        </section>
      </div>`;
    },
  };

  function show(id) {
    document.querySelectorAll("#dash-nav button").forEach((b) => b.classList.toggle("on", b.dataset.id === id));
    $("dash-main").innerHTML = views[id]();
    history.replaceState({}, "", "#/" + id);
  }

  document.addEventListener("DOMContentLoaded", () => {
    $("dash-nav").innerHTML = TABS.map(
      ([id, label]) => `<button data-id="${id}">${label}</button>`
    ).join("");
    $("dash-nav").addEventListener("click", (e) => {
      const b = e.target.closest("button[data-id]");
      if (b) show(b.dataset.id);
    });
    const start = (location.hash || "").replace("#/", "") || "salud";
    show(views[start] ? start : "salud");
  });
})();
