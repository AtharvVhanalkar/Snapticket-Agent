document.addEventListener("DOMContentLoaded", async () => {
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("file-input");
  const preview = document.getElementById("image-preview");
  const previewContainer = document.getElementById("preview-container");
  const analyzeBtn = document.getElementById("analyze-btn");
  const dispatchBtn = document.getElementById("dispatch-btn");
  let selectedFile = null;

  // Check for recent crash reports
  try {
    const res = await fetch("/api/detect-telemetry");
    const data = await res.json();
    const statusEl = document.getElementById("telemetry-status");
    const iconEl = document.getElementById("telemetry-icon");
    if (data.detected) {
      statusEl.innerText = `Detected incident: ${data.incident.filename}`;
      statusEl.classList.add("text-emerald-600");
      iconEl.className = "w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center";
      iconEl.innerHTML = '<i class="fa-solid fa-check"></i>';
    } else {
      statusEl.innerText = "No recent crash reports found in ~/Library/Logs.";
    }
  } catch (e) {
    console.log("Telemetry check skipped");
  }

  dropzone.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length) {
      selectedFile = e.target.files[0];
      preview.src = URL.createObjectURL(selectedFile);
      previewContainer.classList.remove("hidden");
    }
  });

  analyzeBtn.addEventListener("click", async () => {
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';
    
    const formData = new FormData();
    const privacyChoice = document.querySelector('input[name="privacy-choice"]:checked').value;
    if (selectedFile && privacyChoice === "full") {
      formData.append("image", selectedFile);
    }
    formData.append("use_telemetry", document.getElementById("use-telemetry-toggle").checked);

    try {
      const resp = await fetch("/api/analyze", { method: "POST", body: formData });
      const result = await resp.json();
      document.getElementById("report-title").value = result.structured.title || "Crash Incident";
      document.getElementById("report-markdown").value = result.markdown;
      document.getElementById("analysis-badge").classList.remove("hidden");
    } catch (err) {
      alert("Analysis failed: Ensure Ollama is running or check your API key.");
    } finally {
      analyzeBtn.disabled = false;
      analyzeBtn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Synthesize Bug Report';
    }
  });

  dispatchBtn.addEventListener("click", async () => {
    dispatchBtn.disabled = true;
    dispatchBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Dispatching...';

    const payload = new FormData();
    payload.append("channel", document.querySelector('input[name="channel"]:checked').value);
    payload.append("target", document.getElementById("target-destination").value);
    payload.append("title", document.getElementById("report-title").value);
    payload.append("body", document.getElementById("report-markdown").value);

    try {
      const resp = await fetch("/api/dispatch", { method: "POST", body: payload });
      const result = await resp.json();
      if (result.status === "success") {
        alert(`Issue published successfully!\n\nTarget URL: ${result.url}`);
      } else {
        alert(`Dispatch completed: ${result.message || JSON.stringify(result)}`);
      }
    } catch (err) {
      alert("Dispatch error occurred.");
    } finally {
      dispatchBtn.disabled = false;
      dispatchBtn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Dispatch Issue';
    }
  });
});