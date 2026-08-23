/* LOONA OS — morning briefing, image-only TV, calendar, weather, compact pulse */
(function () {
  const $ = (id) => document.getElementById(id);

  let ttsAudio = null;
  let slideTimer = null;
  let pendingBrief = false;
  let camStream = null;
  let recorder = null;
  let recChunks = [];
  let recording = false;
  let listenLoop = false;
  let voiceRec = null;

  function todayKey() {
    const n = new Date();
    const m = String(n.getMonth() + 1).padStart(2, "0");
    const d = String(n.getDate()).padStart(2, "0");
    return "loona.briefed." + n.getFullYear() + "-" + m + "-" + d;
  }

  function track(name, meta) {
    fetch("/api/event", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, meta: meta || {} }),
    }).catch(() => {});
  }

  function chunkSpeech(text, max) {
    const clean = (text || "").replace(/\s+/g, " ").trim();
    if (!clean) return [];
    const parts = clean.split(/(?<=[.!?])\s+/);
    const out = [];
    let buf = "";
    parts.forEach((p) => {
      if ((buf + " " + p).trim().length > max) {
        if (buf) out.push(buf.trim());
        buf = p;
      } else {
        buf = (buf + " " + p).trim();
      }
    });
    if (buf) out.push(buf.trim());
    return out.length ? out : [clean.slice(0, max)];
  }

  function speakChunk(clean) {
    return new Promise((resolve) => {
      if (ttsAudio) {
        ttsAudio.pause();
        ttsAudio = null;
      }
      const audio = new Audio("/api/tts?text=" + encodeURIComponent(clean));
      audio.crossOrigin = "anonymous";
      ttsAudio = audio;
      if (window.LoonaWorld) window.LoonaWorld.listen(audio);
      const done = () => {
        if (window.LoonaWorld) window.LoonaWorld.silence();
        resolve();
      };
      audio.addEventListener("ended", done, { once: true });
      audio.addEventListener("error", done, { once: true });
      audio.play().catch(() => {
        pendingBrief = true;
        const wake = $("wake");
        if (wake) wake.hidden = false;
        done();
      });
    });
  }

  async function speak(text) {
    const chunks = chunkSpeech(text, 420);
    for (const c of chunks) {
      await speakChunk(c);
    }
  }

  function addMsg(who, text, kind) {
    const box = $("chat-messages");
    const el = document.createElement("div");
    el.className = "message " + (kind || "loona");
    el.innerHTML = `<div class="msg-sender">${who}</div><div class="msg-content"></div>`;
    el.querySelector(".msg-content").textContent = text;
    box.appendChild(el);
    while (box.children.length > 3) box.removeChild(box.firstChild);
    box.scrollTop = box.scrollHeight;
  }

  function tvOn() {
    const tv = $("tv");
    tv.classList.remove("off");
    tv.classList.add("on");
    tv.setAttribute("aria-hidden", "false");
  }
  function tvOff() {
    const tv = $("tv");
    if (!tv.classList.contains("on")) return;
    tv.classList.add("off");
    if (slideTimer) {
      clearInterval(slideTimer);
      slideTimer = null;
    }
    setTimeout(() => {
      tv.classList.remove("on", "off");
      tv.setAttribute("aria-hidden", "true");
    }, 380);
  }

  function mirrorOpen() {
    return $("mirror") && $("mirror").classList.contains("on");
  }

  function setListenLoop(on) {
    listenLoop = !!on;
    if (on && voiceRec) {
      try {
        voiceRec.start();
        $("btn-mic").classList.add("rec");
      } catch (e) {}
    }
  }

  async function openMirror() {
    tvOff();
    const stage = $("mirror");
    stage.classList.remove("off");
    stage.classList.add("on");
    stage.setAttribute("aria-hidden", "false");
    $("btn-capture").classList.add("on");
    $("mirror-title").textContent = "Espejo";
    try {
      if (!camStream) {
        camStream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } },
          audio: true,
        });
      }
      const vid = $("mirror-video");
      vid.srcObject = camStream;
      await vid.play().catch(() => {});
      setListenLoop(true);
      addMsg("LOONA", "Espejo listo. Di foto, graba, o cierra.", "loona");
      speak("Espejo listo. Di foto, graba, o cierra.");
      track("camera_open", {});
    } catch (e) {
      addMsg("LOONA", "No pude abrir la cámara. Permiso en Chrome.", "loona");
      speak("No pude abrir la cámara. Dame permiso en Chrome.");
    }
  }

  function closeMirror() {
    const stage = $("mirror");
    if (!stage.classList.contains("on")) return;
    if (recording) stopRec(true);
    setListenLoop(false);
    if (camStream) {
      camStream.getTracks().forEach((t) => t.stop());
      camStream = null;
    }
    const vid = $("mirror-video");
    if (vid) vid.srcObject = null;
    $("btn-capture").classList.remove("on");
    $("rec-dot").hidden = true;
    stage.classList.add("off");
    setTimeout(() => {
      stage.classList.remove("on", "off");
      stage.setAttribute("aria-hidden", "true");
    }, 380);
  }

  async function saveBlob(blob, kind) {
    const ext = kind === "video" ? "webm" : "jpg";
    const name = "loona-" + kind + "-" + Date.now() + "." + ext;
    const fd = new FormData();
    fd.append("kind", kind);
    fd.append("file", blob, name);
    try {
      const r = await fetch("/api/capture", { method: "POST", body: fd });
      const d = await r.json();
      return d;
    } catch (e) {
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = name;
      a.click();
      return { ok: true, fallback: true, name };
    }
  }

  async function snapPhoto() {
    if (!mirrorOpen()) await openMirror();
    const vid = $("mirror-video");
    if (!vid || !vid.videoWidth) {
      speak("Aún no veo el espejo.");
      return;
    }
    const c = document.createElement("canvas");
    c.width = vid.videoWidth;
    c.height = vid.videoHeight;
    const g = c.getContext("2d");
    g.translate(c.width, 0);
    g.scale(-1, 1);
    g.drawImage(vid, 0, 0);
    const flash = $("mirror-flash");
    flash.style.animation = "none";
    void flash.offsetWidth;
    flash.style.animation = "tvflash 0.35s ease-out";
    const blob = await new Promise((res) => c.toBlob(res, "image/jpeg", 0.92));
    const saved = await saveBlob(blob, "photo");
    track("photo", { name: saved && saved.name });
    addMsg("LOONA", "Foto guardada.", "loona");
    speak("Listo. Foto guardada.");
  }

  function startRec() {
    if (!camStream) {
      openMirror().then(() => startRec());
      return;
    }
    if (recording) {
      speak("Ya estoy grabando.");
      return;
    }
    recChunks = [];
    const mime = MediaRecorder.isTypeSupported("video/webm;codecs=vp9,opus")
      ? "video/webm;codecs=vp9,opus"
      : "video/webm";
    try {
      recorder = new MediaRecorder(camStream, { mimeType: mime });
    } catch (e) {
      recorder = new MediaRecorder(camStream);
    }
    recorder.ondataavailable = (ev) => {
      if (ev.data && ev.data.size) recChunks.push(ev.data);
    };
    recorder.onstop = async () => {
      const blob = new Blob(recChunks, { type: recorder.mimeType || "video/webm" });
      const saved = await saveBlob(blob, "video");
      track("video", { name: saved && saved.name });
      addMsg("LOONA", "Video guardado.", "loona");
      speak("Video guardado.");
    };
    recorder.start(250);
    recording = true;
    $("rec-dot").hidden = false;
    $("mirror-title").textContent = "Grabando";
    addMsg("LOONA", "Grabando. Di para, cuando termines.", "loona");
    speak("Grabando.");
  }

  function stopRec(silent) {
    if (!recording || !recorder) return;
    recording = false;
    $("rec-dot").hidden = true;
    $("mirror-title").textContent = "Espejo";
    try {
      recorder.stop();
    } catch (e) {}
    if (silent) speak("");
  }

  function projectImages(items, title) {
    $("tv-title").textContent = title || "IA · HOY";
    const pics = (items || []).filter((it) => it.image);
    if (!pics.length) {
      $("tv-body").innerHTML = '<div class="cinema"><div class="empty">SIN IMAGEN EN EL FEED</div></div>';
      tvOn();
      return;
    }
    $("tv-body").innerHTML =
      '<div class="cinema">' +
      pics
        .map(
          (it, i) =>
            `<figure class="slide ${i === 0 ? "on" : ""}"><img src="${it.image}" alt="" /></figure>`
        )
        .join("") +
      "</div>";
    tvOn();
    if (slideTimer) clearInterval(slideTimer);
    if (pics.length < 2) return;
    let n = 0;
    slideTimer = setInterval(() => {
      const slides = $("tv-body").querySelectorAll(".slide");
      if (!slides.length) return;
      slides[n].classList.remove("on");
      n = (n + 1) % slides.length;
      slides[n].classList.add("on");
    }, 4200);
  }

  function tickClock() {
    const el = $("hud-clock");
    if (!el) return;
    const n = new Date();
    el.textContent =
      String(n.getHours()).padStart(2, "0") + ":" + String(n.getMinutes()).padStart(2, "0");
  }

  async function loadWeather() {
    try {
      const r = await fetch("/api/weather");
      const d = await r.json();
      $("wx-temp").textContent = d.temp != null ? d.temp + "°" : "—°";
      $("wx-label").textContent = d.label || "Monterrey";
      const bits = [];
      if (d.high != null && d.low != null) bits.push(d.low + "° / " + d.high + "°");
      if (d.humidity != null) bits.push(d.humidity + "%");
      $("wx-span").textContent = bits.join(" · ");
      const chip = $("hud-wx");
      if (chip && d.temp != null) chip.textContent = d.temp + "° MTY";
    } catch (e) {
      $("wx-label").textContent = "Sin clima";
    }
  }

  async function loadCalendar() {
    try {
      const r = await fetch("/api/calendar");
      const d = await r.json();
      $("cal-month").textContent = d.month_title || d.month || "Agenda";
      $("cal-dow").innerHTML = (d.dow || ["L", "M", "X", "J", "V", "S", "D"])
        .map((x) => "<span>" + x + "</span>")
        .join("");
      $("cal-grid").innerHTML = (d.cells || [])
        .map((c) => {
          if (!c.d) return '<div class="cal-cell empty"></div>';
          const cls = ["cal-cell"];
          if (c.today) cls.push("today");
          if (c.dots) cls.push("has");
          return `<div class="${cls.join(" ")}" title="${(c.titles || []).join(", ")}">${c.d}</div>`;
        })
        .join("");
      const up = d.upcoming || [];
      $("cal-up").innerHTML = up.length
        ? up
            .map(
              (it) =>
                `<div class="up-item"><time>${it.when}</time><p>${it.title}</p></div>`
            )
            .join("")
        : '<div class="up-item"><p>Nada próximo.</p></div>';
    } catch (e) {
      $("cal-month").textContent = "Agenda";
    }
  }

  async function runMorningBriefing(force) {
    try {
      const r = await fetch("/api/briefing");
      const d = await r.json();
      projectImages(d.news, "IA · HOY");
      addMsg("LOONA", d.speech || "Buenos días.", "loona");
      track("briefing", { n: (d.news || []).length, force: !!force });
      await speak(d.speech);
      localStorage.setItem(todayKey(), "1");
    } catch (e) {
      addMsg("LOONA", "No pude armar el briefing de la mañana.", "loona");
    }
  }

  function showTelegram() {
    $("tv-title").textContent = "TELEGRAM";
    $("tv-body").innerHTML = "";
    tvOn();
    fetch("/api/telegram/status")
      .then((r) => r.json())
      .then((d) => {
        $("tv-body").innerHTML = d.configured
          ? '<div class="cinema"><div class="empty">CANAL LISTO</div></div>'
          : '<div class="cinema"><div class="empty">FALTA TELEGRAM_BOT_TOKEN EN RUNTIME/.ENV</div></div>';
      })
      .catch(() => {
        $("tv-body").innerHTML = '<div class="cinema"><div class="empty">RUNTIME CAÍDO</div></div>';
      });
  }

  async function sendChat(text) {
    if (!text) return;
    addMsg("TÚ", text, "you");
    const low = text.toLowerCase();
    if (/cierra( la)? c[aá]mara|cierra( el)? espejo/.test(low)) {
      closeMirror();
      return;
    }
    if (/cierra|apaga|oculta/.test(low)) {
      closeMirror();
      tvOff();
      return;
    }
    if (/(deja de grabar|para( de)? grabar|para el video|det[eé]n( el)? video|stop)/.test(low) && recording) {
      return stopRec();
    }
    if (/\b(foto|selfie|t[oó]ma(me)?( una)? foto|captura( foto)?)\b/.test(low)) {
      return snapPhoto();
    }
    if (/\b(graba|video|empieza a grabar|recording)\b/.test(low)) {
      if (!mirrorOpen()) return openMirror().then(startRec);
      return startRec();
    }
    if (/\b(espejo|c[aá]mara|capture|captura)\b/.test(low)) {
      return openMirror();
    }
    if (/noticia|titular|news|mañana|buenos días|briefing/.test(low)) {
      return runMorningBriefing(true);
    }
    if (/agenda|calendario/.test(low)) return loadCalendar();
    if (/telegram/.test(low)) return showTelegram();
    try {
      const r = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      const data = await r.json();
      if (!r.ok) {
        addMsg("LOONA", data.detail || data.error || "No pude responder.", "loona");
        return;
      }
      addMsg("LOONA", data.reply, "loona");
      speak(data.reply);
    } catch (e) {
      addMsg("LOONA", "Sin runtime.", "loona");
    }
  }

  function bindVoice() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const btn = $("btn-mic");
    if (!SR) {
      btn.title = "Este navegador no trae reconocimiento de voz";
      return;
    }
    const rec = new SR();
    voiceRec = rec;
    rec.lang = "es-MX";
    rec.interimResults = false;
    rec.continuous = false;
    rec.onresult = (ev) => {
      const said = (ev.results[0][0].transcript || "").trim();
      const wake = /^(ok\s+|okay\s+|oye\s+|hey\s+)?(loona|luna|lona)\b/i;
      if (listenLoop) {
        if (!wake.test(said)) return;
        const rest = said.replace(wake, "").replace(/^[,.\s]+/, "").trim();
        if (!rest) {
          sendChat("estoy aquí");
          return;
        }
        if (/\b(luz|foco|ves|mira)\b/i.test(rest)) {
          fetch("/api/pet", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: rest }),
          }).catch(() => {});
          return;
        }
        sendChat(rest);
        return;
      }
      sendChat(said);
    };
    rec.onend = () => {
      btn.classList.remove("rec");
      if (listenLoop) {
        setTimeout(() => {
          if (!listenLoop) return;
          try {
            rec.start();
            btn.classList.add("rec");
          } catch (e) {}
        }, 220);
      }
    };
    const start = () => {
      btn.classList.add("rec");
      try {
        rec.start();
      } catch (e) {}
    };
    btn.addEventListener("mousedown", start);
    btn.addEventListener("touchstart", start);
    document.addEventListener("keydown", (e) => {
      if (e.code === "Space" && document.activeElement.id !== "chat-input") {
        e.preventDefault();
        start();
      }
    });
  }

  async function loadConfig() {
    try {
      const r = await fetch("/api/config");
      if (!r.ok) return;
      const cfg = await r.json();
      if (window.LoonaWorld) window.LoonaWorld.apply(cfg.world);
      const map = {
        "cfg-particleCount": cfg.world && cfg.world.particleCount,
        "cfg-paletteFrom": cfg.world && cfg.world.paletteFrom,
        "cfg-paletteTo": cfg.world && cfg.world.paletteTo,
        "cfg-headMorph": cfg.world && cfg.world.headMorph,
        "cfg-provider": cfg.brain && cfg.brain.provider,
        "cfg-model": cfg.brain && cfg.brain.model,
      };
      Object.entries(map).forEach(([id, val]) => {
        const el = $(id);
        if (el && val != null) el.value = val;
      });
      if (cfg.guardrails) $("cfg-sandbox").checked = !!cfg.guardrails.sandbox;
      if ($("val-particleCount") && $("cfg-particleCount")) {
        $("val-particleCount").textContent = $("cfg-particleCount").value;
      }
    } catch (e) {}
  }

  function bindConfig() {
    $("cfg-particleCount").addEventListener("input", () => {
      $("val-particleCount").textContent = $("cfg-particleCount").value;
    });
    $("btn-save-config").addEventListener("click", async () => {
      const body = {
        world: {
          particleCount: +$("cfg-particleCount").value,
          paletteFrom: $("cfg-paletteFrom").value,
          paletteTo: $("cfg-paletteTo").value,
          headMorph: $("cfg-headMorph").value,
        },
        brain: {
          provider: $("cfg-provider").value,
          model: $("cfg-model").value,
        },
        guardrails: { sandbox: $("cfg-sandbox").checked },
      };
      try {
        await fetch("/api/config", {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        if (window.LoonaWorld) window.LoonaWorld.apply(body.world);
        addMsg("LOONA", "Controles aplicados.", "loona");
      } catch (e) {
        if (window.LoonaWorld) window.LoonaWorld.apply(body.world);
      }
    });
  }

  function bindChrome() {
    $("chat-form").addEventListener("submit", (e) => {
      e.preventDefault();
      const t = $("chat-input").value.trim();
      $("chat-input").value = "";
      sendChat(t);
    });
    $("btn-capture").addEventListener("click", () => {
      if (mirrorOpen()) closeMirror();
      else openMirror();
    });
    $("btn-mirror-close").addEventListener("click", closeMirror);
    $("btn-snap").addEventListener("click", snapPhoto);
    $("btn-rec").addEventListener("click", () => {
      if (recording) stopRec();
      else startRec();
    });
    const crew = $("crew");
    if (crew) {
      crew.addEventListener("click", (e) => {
        const b = e.target.closest("button[data-agent]");
        if (!b) return;
        crew.querySelectorAll("button").forEach((x) => x.classList.toggle("on", x === b));
        if (window.LoonaWorld && window.LoonaWorld.highlight) {
          window.LoonaWorld.highlight(b.getAttribute("data-agent"));
        }
        const id = b.dataset.agent;
        if (id === "agenda") return loadCalendar();
        if (id === "salud" || id === "dinero") {
          window.location.href = "/dash.html#/" + (id === "dinero" ? "finanzas" : "salud");
          return;
        }
        if (id === "social") return showTelegram();
        sendChat("Eres el agente " + id + " de LOONA. Preséntate en una frase y dime qué puedes hacer hoy.");
      });
    }
    $("btn-dash").addEventListener("click", () => {
      window.location.href = "/dash.html";
    });
    $("btn-brief").addEventListener("click", () => runMorningBriefing(true));
    $("btn-cal").addEventListener("click", loadCalendar);
    $("btn-tg").addEventListener("click", showTelegram);
    $("btn-tv-close").addEventListener("click", tvOff);
    $("btn-config").addEventListener("click", () => $("drawer").classList.add("open"));
    $("btn-drawer-close").addEventListener("click", () => $("drawer").classList.remove("open"));
    $("btn-knowledge").addEventListener("click", async () => {
      $("knowledge").classList.add("open");
      try {
        const r = await fetch("/api/knowledge");
        const d = await r.json();
        let t = d.soul || "";
        t = t.replace(/^### (.*)$/gm, "<h2>$1</h2>");
        t = t.replace(/^## (.*)$/gm, "<h2>$1</h2>");
        t = t.replace(/^# (.*)$/gm, "<h1>$1</h1>");
        t = t.replace(/\n/g, "<br/>");
        $("knowledge-body").innerHTML = t;
      } catch (e) {
        $("knowledge-body").textContent = "Sin knowledge.";
      }
    });
    $("btn-close-knowledge").addEventListener("click", () => $("knowledge").classList.remove("open"));
    $("btn-wake").addEventListener("click", () => {
      $("wake").hidden = true;
      if (pendingBrief) {
        pendingBrief = false;
        runMorningBriefing(true);
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    tickClock();
    setInterval(tickClock, 15000);
    loadCalendar();
    loadWeather();
    bindChrome();
    bindVoice();
    bindConfig();
    loadConfig();
    track("session_start", {});
    const firstToday = !localStorage.getItem(todayKey());
    if (firstToday) {
      runMorningBriefing(false);
    }
  });
})();
