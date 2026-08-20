/* C.A.W.L. shell — comms line to the Archmagos. */
(function () {
  "use strict";

  var $ = function (s) { return document.querySelector(s); };

  var transcript = $("#transcript");
  var emptyState = $("#empty-state");
  var form = $("#composer");
  var input = $("#prompt");
  var sendBtn = $("#send");
  var statusText = $("#status-text");
  var modelMeta = $("#model-meta");
  var readout = $("#readout");
  var cawlImg = $("#cawl-img");
  var settingsModal = $("#settings-modal");
  var settingsBody = $("#settings-body");
  var settingsNote = $("#settings-note");
  var settingsSave = $("#settings-save");
  var voxCallBtn = $("#vox-call");
  var audio = new Audio();
  var lastSettings = null;

  var modes = { deepthink: false, webfetch: false, verify: false };

  function restoreIdle() {
    if (!sendBtn.disabled) {
      statusText.textContent = "cogitators ready";
    }
  }
  audio.addEventListener("playing", function () {
    document.body.classList.add("speaking");
    statusText.textContent = "voice rune active · speaking";
  });
  audio.addEventListener("ended", function () {
    document.body.classList.remove("speaking");
    restoreIdle();
  });
  audio.addEventListener("error", function () {
    document.body.classList.remove("speaking");
    restoreIdle();
  });

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function now() {
    return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  function scrollBottom() {
    var sc = document.querySelector(".transcript-scroll");
    sc.scrollTop = sc.scrollHeight;
  }

  function addMsg(role, text) {
    emptyState.hidden = true;
    var time = now();
    var li = document.createElement("li");
    li.className = "msg " + role;
    if (role === "cawl") {
      li.innerHTML =
        '<div class="src"><span class="glyph"></span>ARCHMAGOS <time>' + time + "</time></div>" +
        '<p class="bubble"></p>';
      li.querySelector(".bubble").textContent = text;
      makeReplayable(li);
    } else {
      li.innerHTML = '<p class="bubble"></p><time>' + time + "</time>";
      li.querySelector(".bubble").textContent = text;
    }
    transcript.appendChild(li);
    scrollBottom();
    return li;
  }

  function addTyping() {
    emptyState.hidden = true;
    var li = document.createElement("li");
    li.className = "msg cawl typing";
    li.innerHTML =
      '<div class="src"><span class="glyph"></span>ARCHMAGOS</div>' +
      '<p class="bubble"><i></i><i></i><i></i></p>';
    transcript.appendChild(li);
    scrollBottom();
    return li;
  }

  function addTools(tools) {
    if (!tools || !tools.length) return;
    var ul = document.createElement("ul");
    ul.className = "tools";
    tools.forEach(function (t) {
      var arg = String(t.arg || "").length > 44
        ? String(t.arg).slice(0, 44) + "…"
        : String(t.arg || "");
      var li = document.createElement("li");
      li.innerHTML =
        '<span class="t-verb">▶ ' + esc(t.verb) + "</span>::" + esc(arg) +
        ' <b class="' + (t.ok ? "ok" : "no") + '">' + (t.ok ? "✓" : "✗") + "</b>";
      ul.appendChild(li);
    });
    transcript.appendChild(ul);
    scrollBottom();
  }

  function makeReplayable(li) {
    var bubble = li.querySelector(".bubble");
    if (!bubble) return;
    bubble.classList.add("replayable");
    bubble.addEventListener("click", function () {
      speak(bubble.textContent);
    });
  }

  function parseJson(r) {
    return r.text().then(function (t) {
      try { return JSON.parse(t); }
      catch (e) { return { detail: "malformed server response" }; }
    });
  }

  function postJson(url, body, timeoutMs) {
    var ctrl = new AbortController();
    var timer = setTimeout(function () { ctrl.abort(); }, timeoutMs);
    return fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: ctrl.signal
    }).finally(function () { clearTimeout(timer); });
  }

  function speak(text) {
    if (!text) return;
    audio.pause();
    postJson("/say", { entry: text.slice(0, 2000) }, 60000)
      .then(parseJson)
      .then(function (d) {
        if ((d.format === "mp3" || d.format === "wav") && d.url) {
          audio.src = d.url;
          audio.play().catch(function () {});
        }
      })
      .catch(function () {});
  }

  var thinkTimer = null;
  var thinkStart = 0;

  function setThinking(on) {
    document.body.classList.toggle("thinking", on);
    sendBtn.disabled = on;
    clearInterval(thinkTimer);
    if (on) {
      thinkStart = Date.now();
      statusText.textContent = "cogitators pondering…";
      readout.textContent = "COGITATORS PONDERING · MOTIVE FORCE 100%";
      thinkTimer = setInterval(function () {
        var s = Math.round((Date.now() - thinkStart) / 1000);
        statusText.textContent = "cogitators pondering · " + s + "s";
      }, 1000);
    } else {
      statusText.textContent = "cogitators ready";
      readout.textContent = "MOTIVE FORCE 100% · LATTICE STABLE · VERIFY > ASSERT";
    }
  }

  function ask(text) {
    addMsg("user", text);
    input.value = "";
    var typing = addTyping();
    setThinking(true);
    postJson("/chat", { message: text, deepthink: modes.deepthink, webfetch: modes.webfetch, verify: modes.verify }, 150000)
      .then(function (r) {
        return parseJson(r).then(function (d) { return { ok: r.ok, status: r.status, data: d }; });
      })
      .then(function (res) {
        typing.remove();
        if (!res.ok) {
          addMsg("cawl", "The cogitator spits error — " + (res.data.detail || ("server returned " + res.status)) + ".");
        } else {
          var reply = res.data.reply || "…silence.";
          if (modes.deepthink && res.data.thinking) {
            reply = "[THOUGHT PROCESS]\n" + res.data.thinking + "\n[/THOUGHT PROCESS]\n\n" + reply;
          }
          addMsg("cawl", reply);
          addTools(res.data.tools);
          if (res.data.reply) speak(res.data.reply);
        }
      })
      .catch(function (err) {
        typing.remove();
        addMsg("cawl", (err && err.name === "AbortError")
          ? "The cogitator still ponders — the free machine-spirit is slow today. Give it another moment, Void Dragon."
          : "Link failure. The Motive Force is interrupted — " + (err && err.message) + ".");
      })
      .finally(function () { setThinking(false); });
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var t = input.value.trim();
    if (t && !sendBtn.disabled) ask(t);
  });

  document.querySelectorAll(".mode-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var key = btn.id.replace("-btn", "");
      modes[key] = !modes[key];
      btn.classList.toggle("active", modes[key]);
      var label = key === "deepthink" ? "THINK" : key === "webfetch" ? "FETCH" : "VERIFY";
      statusText.textContent = label + " " + (modes[key] ? "engaged" : "disengaged");
      setTimeout(function () { if (!sendBtn.disabled) statusText.textContent = "cogitators ready"; }, 1500);
    });
  });

  document.querySelectorAll(".chip").forEach(function (chip) {
    chip.addEventListener("click", function () {
      input.value = chip.textContent.trim();
      input.focus();
    });
  });

  // ---- Vox depth controls (pitch / depth) in the presence panel ----
  var pitchRange = $("#vox-pitch");
  var depthRange = $("#vox-depth");
  var pitchVal = $("#vox-pitch-val");
  var depthVal = $("#vox-depth-val");
  var depthTimer = null;

  function setDepthSliders(st) {
    if (!st || !st.voice) return;
    var p = Number(st.voice.kokoro_pitch);
    var d = Number(st.voice.kokoro_depth);
    if (!isNaN(p)) { pitchRange.value = p; pitchVal.textContent = p.toFixed(2); }
    if (!isNaN(d)) { depthRange.value = d; depthVal.textContent = d.toFixed(2); }
  }

  function persistDepth() {
    clearTimeout(depthTimer);
    depthTimer = setTimeout(function () {
      postJson("/settings", {
        patch: {
          KOKORO_PITCH: pitchRange.value,
          KOKORO_DEPTH: depthRange.value
        }
      }, 20000).catch(function () {});
    }, 400);
  }

  pitchRange.addEventListener("input", function () {
    pitchVal.textContent = pitchRange.value;
    persistDepth();
  });
  depthRange.addEventListener("input", function () {
    depthVal.textContent = depthRange.value;
    persistDepth();
  });
  [pitchRange, depthRange].forEach(function (r) {
    r.addEventListener("change", function () {
      pitchVal.textContent = pitchRange.value;
      depthVal.textContent = depthRange.value;
      postJson("/settings", {
        patch: {
          KOKORO_PITCH: pitchRange.value,
          KOKORO_DEPTH: depthRange.value
        }
      }, 20000)
        .then(parseJson)
        .then(function () { speak("The Machine has been tuned, Void Dragon."); })
        .catch(function () {});
    });
  });

  // ---- Voice call mode (free browser speech recognition -> /chat -> speak) ----
  var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  var voxLive = false;
  var voxRec = null;
  var voxRestartTimer = null;

  function voxListen() {
    if (!voxLive) return;
    if (sendBtn.disabled) {  // a query is in flight — wait for it
      voxRestartTimer = setTimeout(voxListen, 500);
      return;
    }
    try {
      voxRec = new SR();
      voxRec.lang = "en-US";
      voxRec.continuous = true;
      voxRec.interimResults = false;
      voxRec.onresult = function (e) {
        for (var i = e.resultIndex; i < e.results.length; i++) {
          var t = e.results[i][0].transcript.trim();
          if (t) { voxRec.stop(); ask(t); return; }
        }
      };
      voxRec.onend = function () {
        voxRec = null;
        voxRestartTimer = setTimeout(voxListen, 350);
      };
      voxRec.onerror = function (ev) {
        if (ev.error === "not-allowed" || ev.error === "service-not-allowed") {
          endVoxCall();
          statusText.textContent = "vox call muted — mic access denied";
        }
      };
      voxRec.start();
    } catch (err) {
      endVoxCall();
      statusText.textContent = "vox call unavailable — browser has no speech recognition";
    }
  }

  function endVoxCall() {
    voxLive = false;
    clearTimeout(voxRestartTimer);
    if (voxRec) { try { voxRec.stop(); } catch (e) {} voxRec = null; }
    voxCallBtn.classList.remove("live");
    voxCallBtn.textContent = "VOX CALL";
    document.body.classList.remove("vox-live");
    if (!sendBtn.disabled) statusText.textContent = "cogitators ready";
  }

  function startVoxCall() {
    voxLive = true;
    voxCallBtn.classList.add("live");
    voxCallBtn.textContent = "END VOX";
    document.body.classList.add("vox-live");
    statusText.textContent = "vox call live — speak to the Machine";
    voxListen();
  }

  voxCallBtn.addEventListener("click", function () {
    if (voxLive) { endVoxCall(); return; }
    if (!SR) {
      statusText.textContent = "vox call unavailable — this browser has no speech recognition";
      return;
    }
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(function (stream) {
          stream.getTracks().forEach(function (t) { t.stop(); });
          startVoxCall();
        })
        .catch(function () {
          statusText.textContent = "vox call blocked — mic permission denied";
        });
    } else {
      startVoxCall();
    }
  });

  function applyAvatar(st) {
    cawlImg.onerror = function () {
      cawlImg.hidden = true;
      $(".cawl-svg").hidden = false;
    };
    cawlImg.src = "/avatar?" + Date.now();
    cawlImg.hidden = false;
    $(".cawl-svg").hidden = true;
  }

  function field(key, type, label, value, opts) {
    opts = opts || {};
    var inp;
    if (type === "select") {
      var o = (opts.opts || []).map(function (p) {
        return '<option value="' + esc(p[0]) + '"' + (String(value) === String(p[0]) ? " selected" : "") + ">" + esc(p[1]) + "</option>";
      }).join("");
      inp = '<select data-key="' + key + '">' + o + "</select>";
    } else {
      var attrs = 'data-key="' + key + '" type="' + type + '" value="' + esc(value == null ? "" : value) + '"';
      if (opts.step) attrs += ' step="' + opts.step + '"';
      if (opts.min) attrs += ' min="' + opts.min + '"';
      if (opts.max) attrs += ' max="' + opts.max + '"';
      inp = "<input " + attrs + ">";
    }
    return '<div class="set-row"><label>' + esc(label) + "</label>" + inp +
      (opts.hint ? '<span class="hint">' + opts.hint + "</span>" : "") + "</div>";
  }

  function checkRow(key, label, checked) {
    return '<div class="set-row"><label class="set-check"><input type="checkbox" data-key="' + key + '"' + (checked ? " checked" : "") + "> " + esc(label) + "</label></div>";
  }

  function keyRow(name, meta, value) {
    var isCli = name === "opencode";
    var noKey = meta.has_key;
    var cls = noKey ? "ok" : "no";
    var label = meta.name + ' <span class="set-key ' + cls + '"><span class="dot-mini"></span>' +
      (noKey ? (meta.needs_key ? "KEY SET" : "NO KEY NEEDED") : "NO KEY") + "</span>";
    var hint = isCli
      ? "CLI name on PATH (leave blank for opencode). It must be logged in: opencode auth login."
      : meta.needs_key
        ? "Paste your " + esc(meta.key_label) + " here. Blank = keep the stored key."
        : "No key required — free anonymous tier. Optional key overrides the gateway.";
    return '<div class="set-row"><label>' + label + "</label>" +
      '<input type="text" data-key="' + (isCli ? "OPENCODE_CLI" : meta.key_label) + '"' +
      (isCli ? ' placeholder="opencode"' : ' placeholder="' + esc(meta.key_label) + '"') + ">" +
      '<span class="hint">' + hint + "</span></div>";
  }

  function buildForm(st) {
    var html = "";

    html += '<section class="set-group"><h3>Machine Spirit · Brain</h3>';
    html += field("BRAIN_PROVIDER", "select", "Provider", st.provider, {
      opts: [
        ["auto", "auto — first provider with a key"],
        ["opencode", "opencode CLI (local)"],
        ["openrouter", "OpenRouter"],
        ["kilo", "Kilo Code (no key)"],
        ["agnes", "Agnes AI"],
        ["ovh", "OVH AI Endpoints (no key)"],
        ["modelscope", "ModelScope"],
        ["airforce", "Api.Airforce"],
        ["unorouter", "UnoRouter"],
        ["mistral", "Mistral AI"],
        ["groq", "Groq"],
        ["gemini", "Google Gemini"],
        ["nvidia", "NVIDIA NIM"],
        ["offline", "offline — deterministic echo"]
      ]
    });
    html += '<div class="set-row"><span class="hint">Active now: ' + esc(st.provider === "auto" ? "auto (resolves by stored keys)" : st.provider) + "</span></div>";
    html += field("TEMPERATURE", "number", "Temperature", st.temperature, { step: 0.05, min: 0, max: 1.5 });
    html += "</section>";

    html += '<section class="set-group"><h3>Provider Keys &amp; Models</h3>';
    ["openrouter", "kilo", "agnes", "ovh", "modelscope", "airforce", "unorouter",
     "mistral", "groq", "gemini", "nvidia", "opencode"].forEach(function (name) {
      var meta = st.providers[name];
      if (!meta) return;
      html += keyRow(name, meta);
      if (name !== "opencode") {
        var modelKey = { openrouter: "BRAIN_MODEL", mistral: "MISTRAL_MODEL", groq: "GROQ_MODEL", gemini: "GEMINI_MODEL", nvidia: "NVIDIA_MODEL", kilo: "KILO_MODEL", agnes: "AGNES_MODEL", ovh: "OVH_MODEL", modelscope: "MODELSCOPE_MODEL", airforce: "AIRFORCE_MODEL", unorouter: "UNOROUTER_MODEL" }[name];
        html += field(modelKey, "text", "Model (" + meta.name + ")", st.models[name] || "", {});
      }
    });
    html += "</section>";

    html += '<section class="set-group"><h3>Voice</h3>';
    html += field("TTS_ENGINE", "select", "Engine", st.voice_engine, {
      opts: [
        ["auto", "auto"],
        ["kokoro", "kokoro (local, free)"],
        ["elevenlabs", "elevenlabs"],
        ["edge", "edge-tts"],
        ["off", "off"]
      ]
    });
    var vOpts = (st.kokoro_voices || []).length ? (st.kokoro_voices).map(function (v) { return [v, v]; }) : [["am_onyx", "am_onyx"]];
    html += field("KOKORO_VOICE", "select", "Kokoro voice", st.voice.kokoro_voice, { opts: vOpts });
    html += field("KOKORO_SPEED", "number", "Kokoro speed", st.voice.kokoro_speed, { step: 0.01, min: 0.5, max: 1.5 });
    html += field("KOKORO_PITCH", "number", "Kokoro pitch (&gt;1 = deeper)", st.voice.kokoro_pitch, { step: 0.01, min: 0.8, max: 1.5 });
    html += field("KOKORO_DEPTH", "number", "Kokoro depth (machine timbre)", st.voice.kokoro_depth, { step: 0.01, min: 0.5, max: 1.5 });
    html += field("TTS_VOICE", "text", "edge-tts voice", st.voice.tts_voice, {});
    html += field("TTS_RATE", "text", "edge-tts rate", st.voice.tts_rate, {});
    html += field("TTS_PITCH", "text", "edge-tts pitch", st.voice.tts_pitch, {});
    html += field("ELEVENLABS_VOICE_ID", "text", "ElevenLabs voice id", st.voice.elevenlabs_voice_id, {});
    html += field("ELEVENLABS_MODEL", "text", "ElevenLabs model", st.voice.elevenlabs_model, {});
    html += checkRow("VOICE_DSP_ENABLED", "Voice DSP (hardware machine timbre)", st.voice.dsp);
    html += "</section>";

    html += '<section class="set-group"><h3>WorldWideView Integration</h3>';
    html += field("WWV_URL", "text", "WWV URL", st.wwv_url || "http://localhost:3000", {});
    html += field("WWV_ENGINE_URL", "text", "Data Engine URL", st.wwv_engine_url || "http://localhost:5000", {});
    html += field("WWV_API_KEY", "text", "WWV API Key", st.wwv_api_key || "", {});
    html += '<div class="set-row"><span class="hint">Generate API key at WWV setup page → Settings → API Keys. WWV must be running for queries to work.</span></div>';
    html += "</section>";

    html += '<section class="set-group"><h3>Avatar</h3>';
    html += field("AVATAR_IMAGE", "text", "Avatar image path (PNG / JPG on disk)", st.avatar_image, {});
    html += '<div class="set-row"><span class="hint">Absolute path to an image. Leave blank for the SVG machine-spirit figure.</span></div>';
    html += "</section>";

    return html;
  }

  function note(msg, isErr) {
    settingsNote.textContent = msg || "";
    settingsNote.className = "set-save-note" + (isErr ? " error" : "");
  }

  function collectPatch() {
    var patch = {};
    settingsBody.querySelectorAll("[data-key]").forEach(function (el) {
      patch[el.getAttribute("data-key")] = el.type === "checkbox" ? el.checked : el.value.trim();
    });
    return patch;
  }

  function closeSettings() { settingsModal.hidden = true; }

  function openSettings() {
    fetch("/settings")
      .then(parseJson)
      .then(function (st) {
        lastSettings = st;
        settingsBody.innerHTML = buildForm(st);
        note("");
        settingsModal.hidden = false;
        settingsBody.focus();
      })
      .catch(function () {});
  }

  $("#settings-btn").addEventListener("click", openSettings);
  $("#settings-close").addEventListener("click", closeSettings);
  $("#settings-cancel").addEventListener("click", closeSettings);
  settingsModal.addEventListener("click", function (e) {
    if (e.target === settingsModal) closeSettings();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !settingsModal.hidden) closeSettings();
  });

  settingsSave.addEventListener("click", function () {
    settingsSave.disabled = true;
    note("committing to the memory coils…");
    postJson("/settings", { patch: collectPatch() }, 20000)
      .then(parseJson)
      .then(function (d) {
        if (d.detail) throw new Error(d.detail);
        lastSettings = d;
        applyAvatar(d);
        setDepthSliders(d);
        closeSettings();
        refreshStatus();
      })
      .catch(function (err) {
        note("SAVE FAILED — " + (err && err.message ? err.message : "unknown error"), true);
      })
      .finally(function () { settingsSave.disabled = false; });
  });

  function refreshStatus() {
    fetch("/self")
      .then(parseJson)
      .then(function (s) {
        statusText.textContent = s.brain_online
          ? "brain online · " + (s.provider || s.brain) + " · " + (s.research_doctrine || "verify > assert")
          : "brain offline · deterministic echo";
        modelMeta.textContent = "BINHARIC CHANNEL OPEN · "
          + (s.voice_engine === "elevenlabs" ? "ELEVENLABS · DEEP VOICE"
            : s.voice_engine === "kokoro" ? "KOKORO · LOCAL MACHINE SPIRIT" : "EDGE-TTS");
      })
      .catch(function () {});
  }

  function init() {
    refreshStatus();
    fetch("/settings")
      .then(parseJson)
      .then(function (st) {
        applyAvatar(st);
        setDepthSliders(st);
      })
      .catch(function () {});
  }

  init();
})();
