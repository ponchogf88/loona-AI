/* LOONA HUD Apex — Presence Orb (Core + Constellation + Orbital Rings). Updated 2026-08-14. */
(function () {
  const CORE_N = 2200;
  const NODE_N = 110;
  const CREW = [
    { id: "cerebro", x: -3.8, y: 1.7, z: -2.6 },
    { id: "memoria", x: 4.0, y: 1.4, z: -2.3 },
    { id: "ops", x: -4.4, y: -0.3, z: -3.4 },
    { id: "ventas", x: 4.5, y: -0.15, z: -3.1 },
    { id: "salud", x: -2.5, y: -1.9, z: -4.2 },
    { id: "dinero", x: 2.7, y: -2.0, z: -3.9 },
    { id: "agenda", x: -0.15, y: 2.35, z: -4.7 },
    { id: "social", x: 0.35, y: -2.5, z: -4.5 },
  ];

  let scene, camera, renderer, presence;
  let corePts, coreGeo, coreMat, coreRest = [];
  let nodePts, nodeGeo, nodeMat, nodes = [];
  let links, linkGeo, linkMat;
  let crewPoints, crewGeo, crewMat, crewRest = [];
  let speechEnergy = 0;
  let speaking = false;
  let fakePhase = 0;
  let analyser = null;
  let freqData = null;
  let audioCtx = null;
  let hookedAudio = null;
  let lastLevel = 0;
  let activeCrew = "";
  let mouse = { x: 0, y: 0 };
  let look = { x: 0, y: 0 };
  let glow = { x: 0, y: 0 };

  function host() {
    return document.getElementById("world");
  }

  function dotTexture(hex) {
    const c = document.createElement("canvas");
    c.width = 32;
    c.height = 32;
    const g = c.getContext("2d");
    const grd = g.createRadialGradient(16, 16, 0, 16, 16, 16);
    grd.addColorStop(0, hex);
    grd.addColorStop(0.35, "rgba(243,209,154,0.55)");
    grd.addColorStop(1, "rgba(0,0,0,0)");
    g.fillStyle = grd;
    g.fillRect(0, 0, 32, 32);
    const t = new THREE.CanvasTexture(c);
    t.needsUpdate = true;
    return t;
  }

  function onSphere(r, jitter) {
    const u = Math.random();
    const v = Math.random();
    const theta = u * Math.PI * 2;
    const phi = Math.acos(2 * v - 1);
    const rr = r * (1 + (Math.random() - 0.5) * (jitter || 0));
    return {
      x: rr * Math.sin(phi) * Math.cos(theta),
      y: rr * Math.cos(phi),
      z: rr * Math.sin(phi) * Math.sin(theta),
    };
  }

  function inBall(r) {
    const u = Math.random();
    const v = Math.random();
    const theta = u * Math.PI * 2;
    const phi = Math.acos(2 * v - 1);
    const rr = r * Math.pow(Math.random(), 0.45);
    return {
      x: rr * Math.sin(phi) * Math.cos(theta),
      y: rr * Math.cos(phi),
      z: rr * Math.sin(phi) * Math.sin(theta),
    };
  }

  function clearObj(obj) {
    if (!obj || !presence) return;
    presence.remove(obj);
    if (obj.geometry) obj.geometry.dispose();
    if (obj.material) obj.material.dispose();
  }

  function build() {
    if (presence) {
      scene.remove(presence);
    }
    presence = new THREE.Group();
    scene.add(presence);

    coreRest = [];
    coreGeo = new THREE.BufferGeometry();
    const cpos = new Float32Array(CORE_N * 3);
    const ccol = new Float32Array(CORE_N * 3);
    const gold = new THREE.Color("#F3D19A");
    const ice = new THREE.Color("#7DD3FC");
    for (let i = 0; i < CORE_N; i++) {
      const p = inBall(0.48);
      coreRest.push(p);
      cpos[i * 3] = p.x;
      cpos[i * 3 + 1] = p.y;
      cpos[i * 3 + 2] = p.z;
      const t = Math.hypot(p.x, p.y, p.z) / 0.48;
      const col = gold.clone().lerp(ice, t * 0.35);
      ccol[i * 3] = col.r;
      ccol[i * 3 + 1] = col.g;
      ccol[i * 3 + 2] = col.b;
    }
    coreGeo.setAttribute("position", new THREE.BufferAttribute(cpos, 3));
    coreGeo.setAttribute("color", new THREE.BufferAttribute(ccol, 3));
    coreMat = new THREE.PointsMaterial({
      size: 0.038,
      vertexColors: true,
      map: dotTexture("rgba(255,250,235,1)"),
      transparent: true,
      opacity: 0.95,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      sizeAttenuation: true,
    });
    corePts = new THREE.Points(coreGeo, coreMat);
    presence.add(corePts);

    nodes = [];
    nodeGeo = new THREE.BufferGeometry();
    const npos = new Float32Array(NODE_N * 3);
    const ncol = new Float32Array(NODE_N * 3);
    const nodeGold = new THREE.Color("#E8C98A");
    const nodeCyan = new THREE.Color("#5EEAD4");
    const nodeCopper = new THREE.Color("#F59E0B");
    for (let i = 0; i < NODE_N; i++) {
      const layer = i < 28 ? 0.62 : i < 70 ? 0.92 : 1.18;
      const p = onSphere(layer, 0.08);
      nodes.push(p);
      npos[i * 3] = p.x;
      npos[i * 3 + 1] = p.y;
      npos[i * 3 + 2] = p.z;
      const pick = Math.random();
      const col = pick < 0.55 ? nodeCyan : pick < 0.85 ? nodeGold : nodeCopper;
      ncol[i * 3] = col.r;
      ncol[i * 3 + 1] = col.g;
      ncol[i * 3 + 2] = col.b;
    }
    nodeGeo.setAttribute("position", new THREE.BufferAttribute(npos, 3));
    nodeGeo.setAttribute("color", new THREE.BufferAttribute(ncol, 3));
    nodeMat = new THREE.PointsMaterial({
      size: 0.085,
      vertexColors: true,
      map: dotTexture("rgba(190,245,255,1)"),
      transparent: true,
      opacity: 0.95,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      sizeAttenuation: true,
    });
    nodePts = new THREE.Points(nodeGeo, nodeMat);
    presence.add(nodePts);

    const segs = [];
    for (let i = 0; i < NODE_N; i++) {
      const d = [];
      for (let j = 0; j < NODE_N; j++) {
        if (i === j) continue;
        const dx = nodes[i].x - nodes[j].x;
        const dy = nodes[i].y - nodes[j].y;
        const dz = nodes[i].z - nodes[j].z;
        d.push({ j, dist: dx * dx + dy * dy + dz * dz });
      }
      d.sort((a, b) => a.dist - b.dist);
      const kMax = nodes[i].x * nodes[i].x + nodes[i].y * nodes[i].y + nodes[i].z * nodes[i].z > 1 ? 2 : 3;
      for (let k = 0; k < kMax; k++) {
        if (d[k].j < i) continue;
        segs.push(nodes[i], nodes[d[k].j]);
      }
    }
    const lpos = new Float32Array(segs.length * 3);
    for (let i = 0; i < segs.length; i++) {
      lpos[i * 3] = segs[i].x;
      lpos[i * 3 + 1] = segs[i].y;
      lpos[i * 3 + 2] = segs[i].z;
    }
    linkGeo = new THREE.BufferGeometry();
    linkGeo.setAttribute("position", new THREE.BufferAttribute(lpos, 3));
    linkMat = new THREE.LineBasicMaterial({
      color: 0x7dd3fc,
      transparent: true,
      opacity: 0.22,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });
    links = new THREE.LineSegments(linkGeo, linkMat);
    presence.add(links);

    const shell = new THREE.Mesh(
      new THREE.SphereGeometry(1.28, 48, 48),
      new THREE.MeshPhongMaterial({
        color: 0xa8d8ea,
        transparent: true,
        opacity: 0.07,
        shininess: 120,
        specular: 0xffffff,
        side: THREE.DoubleSide,
        depthWrite: false,
      })
    );
    presence.add(shell);

    const wire = new THREE.LineSegments(
      new THREE.WireframeGeometry(new THREE.SphereGeometry(1.26, 18, 14)),
      new THREE.LineBasicMaterial({
        color: 0x94e2f7,
        transparent: true,
        opacity: 0.08,
        depthWrite: false,
      })
    );
    presence.add(wire);

    const ringMat = new THREE.MeshBasicMaterial({
      color: 0xf3d19a,
      transparent: true,
      opacity: 0.28,
      side: THREE.DoubleSide,
      depthWrite: false,
    });
    ringA = new THREE.Mesh(new THREE.TorusGeometry(1.42, 0.008, 8, 80), ringMat);
    ringA.rotation.x = Math.PI / 2.4;
    ringB = new THREE.Mesh(
      new THREE.TorusGeometry(1.52, 0.006, 8, 80),
      new THREE.MeshBasicMaterial({
        color: 0x67e8f9,
        transparent: true,
        opacity: 0.2,
        side: THREE.DoubleSide,
        depthWrite: false,
      })
    );
    ringB.rotation.x = Math.PI / 1.7;
    ringB.rotation.y = 0.6;
    presence.add(ringA);
    presence.add(ringB);

    if (crewPoints && scene) {
      scene.remove(crewPoints);
      if (crewGeo) crewGeo.dispose();
      if (crewMat) crewMat.dispose();
    }
    const per = 380;
    const n = CREW.length * per;
    crewGeo = new THREE.BufferGeometry();
    const cp = new Float32Array(n * 3);
    const cc = new Float32Array(n * 3);
    crewRest = [];
    const mist = new THREE.Color("#9BB0C4");
    for (let k = 0; k < CREW.length; k++) {
      const hub = CREW[k];
      for (let j = 0; j < per; j++) {
        const i = k * per + j;
        const u = Math.random();
        const v = Math.random();
        const theta = u * Math.PI * 2;
        const phi = Math.acos(2 * v - 1);
        const r = 0.38 * Math.pow(Math.random(), 0.55);
        const p = {
          x: hub.x + r * Math.sin(phi) * Math.cos(theta),
          y: hub.y + r * Math.cos(phi) * 0.85,
          z: hub.z + r * Math.sin(phi) * Math.sin(theta),
          id: hub.id,
        };
        crewRest.push(p);
        cp[i * 3] = p.x;
        cp[i * 3 + 1] = p.y;
        cp[i * 3 + 2] = p.z;
        const fade = 0.22 + Math.random() * 0.2;
        cc[i * 3] = mist.r * fade;
        cc[i * 3 + 1] = mist.g * fade;
        cc[i * 3 + 2] = mist.b * fade;
      }
    }
    crewGeo.setAttribute("position", new THREE.BufferAttribute(cp, 3));
    crewGeo.setAttribute("color", new THREE.BufferAttribute(cc, 3));
    crewMat = new THREE.PointsMaterial({
      size: 0.065,
      vertexColors: true,
      map: dotTexture("rgba(200,220,235,1)"),
      transparent: true,
      opacity: 0.5,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      sizeAttenuation: true,
    });
    crewPoints = new THREE.Points(crewGeo, crewMat);
    scene.add(crewPoints);
  }

  let currentMood = "idle";
  let alertEnergy = 0;
  let ringA, ringB;

  function setMood(m) {
    const valid = ["idle", "listen", "speak", "alert"];
    const target = valid.includes(m) ? m : "idle";
    currentMood = target;
    
    if (target === "alert") {
      alertEnergy = 1.0;
    } else if (target === "speak") {
      speaking = true;
    } else {
      speaking = false;
    }

    document.body.classList.remove("is-idle", "is-listening", "is-speaking", "is-alert");
    const statusEl = document.getElementById("hud-status");

    if (target === "idle") {
      document.body.classList.add("is-idle");
      if (statusEl) statusEl.textContent = "IDLE";
    } else if (target === "listen") {
      document.body.classList.add("is-listening");
      if (statusEl) statusEl.textContent = "LISTENING";
    } else if (target === "speak") {
      document.body.classList.add("is-speaking");
      if (statusEl) statusEl.textContent = "SPEAKING";
    } else if (target === "alert") {
      document.body.classList.add("is-alert");
      if (statusEl) statusEl.textContent = "ALERT";
    }
  }

  function band(data, a, b) {
    if (!data) return 0;
    let s = 0;
    const n = Math.min(b, data.length);
    for (let i = a; i < n; i++) s += data[i];
    return n > a ? s / ((n - a) * 255) : 0;
  }

  function readVoice() {
    if (analyser && freqData) {
      analyser.getByteFrequencyData(freqData);
      const bass = band(freqData, 0, 6);
      const mid = band(freqData, 6, 24);
      const high = band(freqData, 24, 72);
      const energy = bass * 0.5 + mid * 0.35 + high * 0.15;
      speechEnergy += (energy - speechEnergy) * 0.32;
      lastLevel = energy;
      return energy;
    }
    if (speaking || currentMood === "speak") {
      fakePhase += 0.16;
      const syllable = Math.abs(Math.sin(fakePhase * 2.2));
      const phrase = 0.45 + 0.55 * Math.abs(Math.sin(fakePhase * 0.32));
      const energy = 0.26 + syllable * phrase * 0.62;
      speechEnergy += (energy - speechEnergy) * 0.2;
      return energy;
    }
    speechEnergy *= 0.9;
    return 0;
  }

  function resize() {
    const el = host();
    if (!el || !camera || !renderer) return;
    const w = el.clientWidth || window.innerWidth;
    const h = el.clientHeight || window.innerHeight;
    camera.aspect = w / Math.max(1, h);
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  }

  function tick() {
    requestAnimationFrame(tick);
    if (!presence) {
      if (renderer && scene && camera) renderer.render(scene, camera);
      return;
    }
    const t = performance.now() * 0.001;
    const talk = readVoice();
    look.x += (mouse.x - look.x) * 0.08;
    look.y += (mouse.y - look.y) * 0.08;
    glow.x += (mouse.x - glow.x) * 0.05;
    glow.y += (mouse.y - glow.y) * 0.05;

    // Decay alert flash
    if (alertEnergy > 0.01) {
      alertEnergy *= 0.95;
    } else {
      alertEnergy = 0;
    }

    const glass = document.getElementById("glass-orb");
    if (glass) {
      const near = Math.hypot(mouse.x, mouse.y) < 0.42;
      glass.style.setProperty("--ox", (look.x * 36).toFixed(2) + "px");
      glass.style.setProperty("--oy", (look.y * 28).toFixed(2) + "px");
      glass.style.setProperty("--nx", (glow.x * 48).toFixed(2) + "px");
      glass.style.setProperty("--ny", (glow.y * 40).toFixed(2) + "px");
      glass.style.setProperty("--px", (look.x * -18).toFixed(2) + "px");
      glass.style.setProperty("--py", (look.y * -14).toFixed(2) + "px");
      glass.style.setProperty("--qx", (glow.x * 58).toFixed(2) + "px");
      glass.style.setProperty("--qy", (glow.y * -42).toFixed(2) + "px");
      glass.style.setProperty("--talk", (talk + alertEnergy * 0.6).toFixed(3));
      glass.style.setProperty("--hov", near ? "1.05" : "1");
    }
    const back = document.getElementById("glass-glow");
    if (back) {
      back.style.setProperty("--bx", (look.x * 22).toFixed(2) + "px");
      back.style.setProperty("--by", (look.y * 18).toFixed(2) + "px");
    }

    // Dynamic state-based expressions (IDLE, LISTEN, SPEAK, ALERT)
    let coreScale = 1.0;
    let ringScale = 1.0;
    let ringOpacity = 0.28;
    let linkOpacity = 0.18;

    if (currentMood === "listen") {
      // LISTENING: pulso suave y atento, anillos más vivos y abiertos
      coreScale = 1.06 + Math.sin(t * 2.5) * 0.035;
      ringScale = 1.16 + Math.sin(t * 1.8) * 0.02;
      ringOpacity = 0.46;
      linkOpacity = 0.32;
    } else if (currentMood === "speak" || speaking) {
      // SPEAKING: núcleo late más con la voz, ondas armónicas
      coreScale = 1.12 + Math.sin(t * 4.5) * 0.06 + talk * 0.12;
      ringScale = 1.12 + talk * 0.18;
      ringOpacity = 0.52 + talk * 0.25;
      linkOpacity = 0.40 + talk * 0.30;
    } else if (currentMood === "alert") {
      // ALERT: destello oro cálido radiante (cero terror, alerta inteligente)
      coreScale = 1.18 + alertEnergy * 0.25 + Math.sin(t * 3.2) * 0.04;
      ringScale = 1.24 + alertEnergy * 0.15;
      ringOpacity = 0.60 + alertEnergy * 0.35;
      linkOpacity = 0.45 + alertEnergy * 0.35;
    } else {
      // IDLE: respiración mínima 24/7
      coreScale = 1.0 + Math.sin(t * 0.75) * 0.016;
      ringScale = 1.0;
      ringOpacity = 0.25;
      linkOpacity = 0.18;
    }

    if (corePts) {
      corePts.scale.setScalar(coreScale);
      coreMat.size = 0.038 + (currentMood === "speak" ? talk * 0.015 : currentMood === "alert" ? alertEnergy * 0.018 : 0);
    }
    if (ringA) {
      ringA.scale.setScalar(ringScale);
      ringA.material.opacity = ringOpacity;
      ringA.rotation.z = t * (currentMood === "listen" ? 0.35 : 0.12);
    }
    if (ringB) {
      ringB.scale.setScalar(ringScale * 1.04);
      ringB.material.opacity = ringOpacity * 0.85;
      ringB.rotation.z = -t * (currentMood === "listen" ? 0.42 : 0.15);
    }
    if (linkMat) linkMat.opacity = linkOpacity;

    presence.rotation.y = t * 0.08 + look.x * 0.45;
    presence.rotation.x = look.y * 0.22;
    presence.position.x = look.x * 0.35;
    presence.position.y = -look.y * 0.22;

    if (crewPoints) {
      const cp = crewGeo.attributes.position.array;
      const spin = t * 0.05;
      const ca = Math.cos(spin);
      const sa = Math.sin(spin);
      for (let i = 0; i < crewRest.length; i++) {
        const p = crewRest[i];
        const i3 = i * 3;
        const on = activeCrew && p.id === activeCrew;
        const s = on ? 1.14 : 1;
        cp[i3] = (p.x * ca - p.z * sa) * s;
        cp[i3 + 1] = p.y * s + Math.sin(t * 0.45 + i * 0.01) * 0.03;
        cp[i3 + 2] = (p.x * sa + p.z * ca) * s;
      }
      crewGeo.attributes.position.needsUpdate = true;
    }

    renderer.render(scene, camera);
  }

  function hookAnalyser(audio) {
    try {
      if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      if (audioCtx.state === "suspended") audioCtx.resume();
      if (!analyser) {
        analyser = audioCtx.createAnalyser();
        analyser.fftSize = 256;
        analyser.smoothingTimeConstant = 0.62;
        freqData = new Uint8Array(analyser.frequencyBinCount);
      }
      if (hookedAudio === audio) return;
      const src = audioCtx.createMediaElementSource(audio);
      src.connect(analyser);
      analyser.connect(audioCtx.destination);
      hookedAudio = audio;
    } catch (e) {
      /* already hooked */
    }
  }

  function listen(audio) {
    setMood("speak");
    fakePhase = 0;
    speechEnergy = Math.max(speechEnergy, 0.35);
    if (audio) {
      audio.crossOrigin = "anonymous";
      hookAnalyser(audio);
      const stop = () => {
        setMood("idle");
      };
      audio.addEventListener("ended", stop, { once: true });
      audio.addEventListener("pause", stop, { once: true });
    }
  }

  function silence() {
    setMood("idle");
  }

  function init() {
    const el = host();
    if (!el || !window.THREE) return;
    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x03040a, 0.038);
    camera = new THREE.PerspectiveCamera(30, 1, 0.1, 80);
    camera.position.set(0, 0.12, 6.6);
    camera.lookAt(0, 0, 0);
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setClearColor(0x000000, 0);
    el.appendChild(renderer.domElement);
    const key = new THREE.PointLight(0xf3d19a, 0.55, 18);
    key.position.set(2.2, 2.4, 4.2);
    scene.add(key);
    scene.add(new THREE.AmbientLight(0x6a7a90, 0.35));
    const fill = new THREE.PointLight(0x67e8f9, 0.28, 14);
    fill.position.set(-2.4, -1.2, 3.2);
    scene.add(fill);
    build();
    resize();
    window.addEventListener("resize", resize);
    window.addEventListener("mousemove", (e) => {
      const box = host();
      const w = (box && box.clientWidth) || window.innerWidth;
      const h = (box && box.clientHeight) || window.innerHeight;
      mouse.x = (e.clientX / w) * 2 - 1;
      mouse.y = (e.clientY / h) * 2 - 1;
    });
    tick();

    const paramMood = new URLSearchParams(window.location.search).get("mood");
    if (paramMood) {
      setMood(paramMood);
    } else if (new URLSearchParams(window.location.search).get("view") === "speaking") {
      setMood("speak");
    } else {
      setMood("idle");
    }
  }

  window.LoonaWorld = {
    apply(world) {},
    setMood,
    getMood() {
      return currentMood;
    },
    listen,
    silence,
    talking() {
      return currentMood === "speak" || speaking;
    },
    level() {
      return speechEnergy;
    },
    highlight(id) {
      activeCrew = id || "";
    },
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
