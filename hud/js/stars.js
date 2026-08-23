/* Sparse SpaceX-like starfield — few points, slow drift, quiet twinkle. */
(function () {
  const COUNT = 48;
  const canvas = () => document.getElementById("stars");
  let ctx, w, h, stars, raf;

  function resize() {
    const c = canvas();
    if (!c) return;
    w = c.width = window.innerWidth;
    h = c.height = window.innerHeight;
  }

  function seed() {
    stars = [];
    for (let i = 0; i < COUNT; i++) {
      stars.push({
        x: Math.random(),
        y: Math.random(),
        z: 0.25 + Math.random() * 0.75,
        s: Math.random() < 0.12 ? 1.35 : 0.55 + Math.random() * 0.55,
        tw: Math.random() * Math.PI * 2,
        sp: 0.18 + Math.random() * 0.35,
        drift: (Math.random() - 0.5) * 0.000012,
      });
    }
  }

  function tick(t) {
    const c = canvas();
    if (!c || !ctx) return;
    ctx.clearRect(0, 0, w, h);
    for (const st of stars) {
      st.tw += st.sp * 0.018;
      st.x += st.drift;
      if (st.x < -0.02) st.x = 1.02;
      if (st.x > 1.02) st.x = -0.02;
      const pulse = 0.28 + 0.72 * Math.abs(Math.sin(st.tw + t * 0.00012));
      const a = 0.18 + pulse * 0.55 * st.z;
      const x = st.x * w;
      const y = st.y * h;
      const r = st.s * (0.7 + st.z);
      ctx.beginPath();
      ctx.fillStyle = "rgba(243, 209, 154," + a.toFixed(3) + ")";
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fill();
      if (st.s > 1.1) {
        ctx.strokeStyle = "rgba(243, 209, 154," + (a * 0.35).toFixed(3) + ")";
        ctx.lineWidth = 0.6;
        ctx.beginPath();
        ctx.moveTo(x - 3.2, y);
        ctx.lineTo(x + 3.2, y);
        ctx.moveTo(x, y - 3.2);
        ctx.lineTo(x, y + 3.2);
        ctx.stroke();
      }
    }
    raf = requestAnimationFrame(tick);
  }

  function init() {
    const c = canvas();
    if (!c) return;
    ctx = c.getContext("2d");
    resize();
    seed();
    window.addEventListener("resize", resize);
    raf = requestAnimationFrame(tick);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
