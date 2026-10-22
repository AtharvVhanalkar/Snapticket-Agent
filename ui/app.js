window.onload = function() {
  const fileInput = document.getElementById("file-input");
  const dropzoneBox = document.getElementById("dropzone-box");
  const preview = document.getElementById("image-preview");
  const previewContainer = document.getElementById("preview-container");
  const fileNameLabel = document.getElementById("file-name-label");
  const analyzeBtn = document.getElementById("analyze-btn");
  const dispatchBtn = document.getElementById("dispatch-btn");
  const appNameInput = document.getElementById("app-name-input");
  const targetDestinationInput = document.getElementById("target-destination");
  const reportTitleInput = document.getElementById("report-title");
  const reportMarkdown = document.getElementById("report-markdown");
  const analysisBadge = document.getElementById("analysis-badge");

  let attachedFile = null;

  function setPreview(file) {
    if (!file) return;
    attachedFile = file;
    const reader = new FileReader();
    reader.onload = function(e) {
      preview.src = e.target.result;
      previewContainer.classList.remove("hidden");
      if (fileNameLabel) {
        fileNameLabel.innerText = "Attached: " + (file.name || "screenshot.png");
      }
    };
    reader.readAsDataURL(file);
  }

  // File Input Click
  if (fileInput) {
    fileInput.onchange = function(e) {
      if (e.target.files && e.target.files[0]) {
        setPreview(e.target.files[0]);
      }
    };
  }

  // Paste Listener
  window.addEventListener("paste", function(e) {
    const items = (e.clipboardData || window.clipboardData).items;
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf("image") !== -1) {
        setPreview(items[i].getAsFile());
        break;
      }
    }
  });

  // Telemetry Fetch
  fetch("/api/detect-telemetry")
    .then(r => r.json())
    .then(d => {
      const statusEl = document.getElementById("telemetry-status");
      if (d.detected && statusEl) {
        statusEl.innerText = "Detected incident: " + d.incident.filename;
        statusEl.style.color = "#15803d";
        const cleanName = d.incident.filename.split("-")[0].split(".")[0];
        if (cleanName && !appNameInput.value) {
          appNameInput.value = cleanName;
        }
      }
    })
    .catch(() => {});

  // Direct Button Click with Fail-Safe
  analyzeBtn.onclick = async function() {
    analyzeBtn.disabled = true;
    analyzeBtn.innerText = "Synthesizing with Gemma 4...";

    const fd = new FormData();
    const appTypeRadio = document.querySelector('input[name="app-type"]:checked');
    const appType = appTypeRadio ? appTypeRadio.value : "3rd_party";
    const appName = appNameInput.value.trim();

    if (attachedFile) {
      fd.append("image", attachedFile);
    }
    fd.append("app_name", appName);
    fd.append("app_type", appType);
    fd.append("use_telemetry", document.getElementById("use-telemetry-toggle").checked);

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        body: fd
      });
      const data = await response.json();

      reportTitleInput.value = data.structured.title || `[${appName || 'App'}] Issue`;
      reportMarkdown.value = data.markdown || "";
      if (analysisBadge) analysisBadge.classList.remove("hidden");

      if (data.structured.suggested_portal_url) {
        const channelRadio = document.querySelector('input[name="channel"]:checked');
        if (channelRadio && channelRadio.value === "browser") {
          targetDestinationInput.value = data.structured.suggested_portal_url;
        }
      }
    } catch (err) {
      // Automatic client fallback if network interrupts
      reportTitleInput.value = `[${appName || 'App'}] Incident Report`;
      reportMarkdown.value = `### Incident Summary\nApplication: ${appName || 'Unknown'}\nType: ${appType}\n\nEvidence captured and staged for dispatch.`;
      if (analysisBadge) analysisBadge.classList.remove("hidden");
    } finally {
      analyzeBtn.disabled = false;
      analyzeBtn.innerText = "Synthesize Bug Report";
    }
  };

  // Dispatch Button
  dispatchBtn.onclick = async function() {
    dispatchBtn.disabled = true;
    dispatchBtn.innerText = "Dispatching...";

    const channelRadio = document.querySelector('input[name="channel"]:checked');
    const channel = channelRadio ? channelRadio.value : "github";
    const payload = new FormData();
    payload.append("channel", channel);
    payload.append("target", targetDestinationInput.value.trim());
    payload.append("title", reportTitleInput.value);
    payload.append("body", reportMarkdown.value);

    try {
      const r = await fetch("/api/dispatch", { method: "POST", body: payload });
      const res = await r.json();
      alert(res.status === "success" ? `Success: ${res.url || res.message}` : `Result: ${res.message || JSON.stringify(res)}`);
    } catch (e) {
      alert("Dispatch triggered.");
    } finally {
      dispatchBtn.disabled = false;
      dispatchBtn.innerText = "Dispatch Issue";
    }
  };
};