/* LOONA Multimodal Live Client — Gemini 2.0 Live API Integration (Voice, Vision, TTS in Real-Time) */
(function () {
  const $ = (id) => document.getElementById(id);

  let ws = null;
  let audioCtx = null;
  let micStream = null;
  let micProcessor = null;
  let videoInterval = null;
  let isLiveActive = false;
  let nextPlayTime = 0;
  let activeAudioSources = [];
  let analyserNode = null;

  function base64ToUint8Array(base64) {
    const binaryString = window.atob(base64);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes;
  }

  function uint8ArrayToBase64(bytes) {
    let binary = '';
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
  }

  function floatTo16BitPCM(input) {
    const output = new Int16Array(input.length);
    for (let i = 0; i < input.length; i++) {
      const s = Math.max(-1, Math.min(1, input[i]));
      output[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
    }
    return output;
  }

  function pcm24kToAudioBuffer(ctx, pcmBytes) {
    const int16 = new Int16Array(pcmBytes.buffer, pcmBytes.byteOffset, pcmBytes.byteLength / 2);
    const audioBuffer = ctx.createBuffer(1, int16.length, 24000);
    const channelData = audioBuffer.getChannelData(0);
    for (let i = 0; i < int16.length; i++) {
      channelData[i] = int16[i] / 32768.0;
    }
    return audioBuffer;
  }

  function stopAllAudioPlayback() {
    activeAudioSources.forEach(src => {
      try { src.stop(); } catch (e) {}
    });
    activeAudioSources = [];
    if (audioCtx) {
      nextPlayTime = audioCtx.currentTime;
    }
  }

  function playPcmChunk(pcmBase64) {
    if (!audioCtx) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioCtx.state === 'suspended') {
      audioCtx.resume();
    }

    if (!analyserNode) {
      analyserNode = audioCtx.createAnalyser();
      analyserNode.fftSize = 64;
      analyserNode.connect(audioCtx.destination);
    }

    try {
      const bytes = base64ToUint8Array(pcmBase64);
      const audioBuffer = pcm24kToAudioBuffer(audioCtx, bytes);
      const source = audioCtx.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(analyserNode);

      const now = audioCtx.currentTime;
      const startTime = Math.max(now, nextPlayTime);
      source.start(startTime);
      nextPlayTime = startTime + audioBuffer.duration;

      activeAudioSources.push(source);
      source.onended = () => {
        const idx = activeAudioSources.indexOf(source);
        if (idx !== -1) activeAudioSources.splice(idx, 1);
        if (activeAudioSources.length === 0 && window.LoonaWorld) {
          window.LoonaWorld.silence();
        }
      };

      if (window.LoonaWorld) {
        window.LoonaWorld.listen({ analyser: analyserNode });
      }
    } catch (err) {
      console.error("[Live] Error decodificando audio PCM:", err);
    }
  }

  function captureVideoFrame() {
    const video = $("mirror-video");
    if (!video || video.paused || video.ended || video.videoWidth === 0) return null;

    const canvas = document.createElement("canvas");
    const scale = 0.5;
    canvas.width = video.videoWidth * scale;
    canvas.height = video.videoHeight * scale;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL("image/jpeg", 0.6);
    return dataUrl.split(",")[1];
  }

  async function startLiveSession(voice = "Aoede") {
    if (isLiveActive) return;

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host || "127.0.0.1:8000";
    const wsUrl = `${protocol}//${host}/api/live/ws?voice=${encodeURIComponent(voice)}`;

    console.log("[Live] Iniciando conexión WebSocket:", wsUrl);
    ws = new WebSocket(wsUrl);

    ws.onopen = async () => {
      console.log("[Live] Conexión abierta con backend");
      isLiveActive = true;
      updateLiveUi(true);

      // Iniciar captura de micrófono (16kHz PCM)
      try {
        if (!audioCtx) {
          audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
        }
        if (audioCtx.state === 'suspended') {
          await audioCtx.resume();
        }

        micStream = await navigator.mediaDevices.getUserMedia({
          audio: {
            channelCount: 1,
            sampleRate: 16000,
            echoCancellation: true,
            noiseSuppression: true
          }
        });

        const micSource = audioCtx.createMediaStreamSource(micStream);
        micProcessor = audioCtx.createScriptProcessor(4096, 1, 1);

        micProcessor.onaudioprocess = (e) => {
          if (!isLiveActive || !ws || ws.readyState !== WebSocket.OPEN) return;
          const inputData = e.inputBuffer.getChannelData(0);
          const pcm16 = floatTo16BitPCM(inputData);
          const pcmBytes = new Uint8Array(pcm16.buffer);
          const b64 = uint8ArrayToBase64(pcmBytes);
          ws.send(JSON.stringify({ type: "audio", data: b64 }));
        };

        micSource.connect(micProcessor);
        micProcessor.connect(audioCtx.destination);
        console.log("[Live] 🎙️ Micrófono transmitiendo a 16kHz PCM");
      } catch (err) {
        console.error("[Live] Error iniciando micrófono:", err);
      }

      // Iniciar captura de video periódica (1 FPS)
      videoInterval = setInterval(() => {
        if (!isLiveActive || !ws || ws.readyState !== WebSocket.OPEN) return;
        const frameB64 = captureVideoFrame();
        if (frameB64) {
          ws.send(JSON.stringify({ type: "image", data: frameB64 }));
        }
      }, 1000);
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "ready") {
          console.log("[Live] Gemini Live listo. Modelo:", msg.model, "Voz:", msg.voice);
          addLiveMsg("LOONA", "✨ Gemini Live conectado. Te escucho y te veo.");
        } else if (msg.type === "audio") {
          playPcmChunk(msg.data);
        } else if (msg.type === "text") {
          addLiveMsg("LOONA", msg.text);
        } else if (msg.type === "interrupted") {
          console.log("[Live] ⚡ Interrupción recibida. Cortando voz de LOONA.");
          stopAllAudioPlayback();
        } else if (msg.type === "error") {
          console.error("[Live] Error del servidor:", msg.message);
          addLiveMsg("LOONA", `⚠️ Error Live: ${msg.message}`);
        }
      } catch (e) {
        console.error("[Live] Error procesando mensaje WS:", e);
      }
    };

    ws.onclose = () => {
      console.log("[Live] Conexión cerrada");
      stopLiveSession();
    };

    ws.onerror = (e) => {
      console.error("[Live] WebSocket error:", e);
      stopLiveSession();
    };
  }

  function stopLiveSession() {
    isLiveActive = false;
    updateLiveUi(false);
    stopAllAudioPlayback();

    if (videoInterval) {
      clearInterval(videoInterval);
      videoInterval = null;
    }
    if (micProcessor) {
      try { micProcessor.disconnect(); } catch (e) {}
      micProcessor = null;
    }
    if (micStream) {
      micStream.getTracks().forEach(t => t.stop());
      micStream = null;
    }
    if (ws) {
      try { ws.close(); } catch (e) {}
      ws = null;
    }
    console.log("[Live] Sesión en vivo detenida.");
  }

  function toggleLiveSession() {
    if (isLiveActive) {
      stopLiveSession();
    } else {
      startLiveSession();
    }
  }

  function updateLiveUi(active) {
    const btn = $("btn-live");
    if (btn) {
      if (active) {
        btn.classList.add("active");
        btn.textContent = "LIVE ●";
        btn.style.color = "#4ef08b";
        btn.style.borderColor = "#4ef08b";
      } else {
        btn.classList.remove("active");
        btn.textContent = "LIVE";
        btn.style.color = "";
        btn.style.borderColor = "";
      }
    }
    const statusEl = $("hud-status");
    if (statusEl) {
      statusEl.textContent = active ? "LIVE STREAM" : "IDLE";
    }
  }

  function addLiveMsg(who, text) {
    const box = $("chat-messages");
    if (!box) return;
    const el = document.createElement("div");
    el.className = "message loona live-msg";
    el.innerHTML = `<div class="msg-sender">${who} <span style="font-size:9px;color:#4ef08b;">● LIVE</span></div><div class="msg-content"></div>`;
    el.querySelector(".msg-content").textContent = text;
    box.appendChild(el);
    while (box.children.length > 4) box.removeChild(box.firstChild);
    box.scrollTop = box.scrollHeight;
  }

  // Exportar al objeto global de LOONA
  window.LoonaLive = {
    start: startLiveSession,
    stop: stopLiveSession,
    toggle: toggleLiveSession,
    isActive: () => isLiveActive
  };

  // Auto-registrar botón LIVE si existe en el DOM
  document.addEventListener("DOMContentLoaded", () => {
    const btnLive = $("btn-live");
    if (btnLive) {
      btnLive.addEventListener("click", toggleLiveSession);
    }
  });
})();
