(() => {
  const urlInput    = document.getElementById("url-input");
  const fetchBtn    = document.getElementById("fetch-btn");
  const downloadBtn = document.getElementById("download-btn");
  const mediaInfo   = document.getElementById("media-info");
  const infoTitle   = document.getElementById("info-title");
  const infoUploader = document.getElementById("info-uploader");
  const infoDuration = document.getElementById("info-duration");
  const formatSelect = document.getElementById("format-select");
  const qualityGroup = document.getElementById("quality-group");
  const thumbnailGroup = document.getElementById("thumbnail-group");
  const thumbnailCheck = document.getElementById("thumbnail-check");
  const statusEl    = document.getElementById("status");
  const toggleBtns  = document.querySelectorAll(".toggle-btn");

  let mediaType = "audio";

  // --- type toggle ---
  toggleBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      toggleBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      mediaType = btn.dataset.type;
      updateFormatOptions();
    });
  });

  function updateFormatOptions() {
    const formats = mediaType === "audio" ? AUDIO_FORMATS : VIDEO_FORMATS;
    formatSelect.innerHTML = formats
      .map(f => `<option value="${f}">${f.toUpperCase()}</option>`)
      .join("");
    qualityGroup.style.display = mediaType === "audio" ? "" : "none";
    thumbnailGroup.style.display = mediaType === "audio" ? "" : "none";
  }

  // --- fetch info ---
  fetchBtn.addEventListener("click", fetchInfo);
  urlInput.addEventListener("keydown", e => { if (e.key === "Enter") fetchInfo(); });

  async function fetchInfo() {
    const url = urlInput.value.trim();
    if (!url) return showStatus("Paste a URL first.", "error");

    fetchBtn.disabled = true;
    showStatus("Fetching info...", "info");
    mediaInfo.classList.add("hidden");

    try {
      const res = await fetch("/info", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to fetch info");

      infoTitle.textContent = data.title;
      infoUploader.textContent = data.uploader;
      infoDuration.textContent = data.duration;
      mediaInfo.classList.remove("hidden");
      hideStatus();
    } catch (err) {
      showStatus(err.message, "error");
    } finally {
      fetchBtn.disabled = false;
    }
  }

  // --- download ---
  downloadBtn.addEventListener("click", async () => {
    const url = urlInput.value.trim();
    if (!url) return showStatus("Paste a URL first.", "error");

    downloadBtn.disabled = true;
    showStatus("⬇️ Downloading... this may take a moment.", "info");

    try {
      const body = {
        url,
        type: mediaType,
        format: formatSelect.value,
        quality: document.getElementById("quality-select")?.value || "192",
        embed_thumbnail: mediaType === "audio" && thumbnailCheck.checked,
      };

      const res = await fetch("/download", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Download failed");
      }

      // Trigger browser file save
      const blob = await res.blob();
      const disposition = res.headers.get("Content-Disposition") || "";
      const nameMatch = disposition.match(/filename="?([^"]+)"?/);
      const filename = nameMatch ? nameMatch[1] : `download.${formatSelect.value}`;

      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = filename;
      a.click();
      URL.revokeObjectURL(a.href);

      showStatus(`✅ Downloaded: ${filename}`, "success");
    } catch (err) {
      showStatus(err.message, "error");
    } finally {
      downloadBtn.disabled = false;
    }
  });

  function showStatus(msg, type) {
    statusEl.textContent = msg;
    statusEl.className = `status ${type}`;
    statusEl.classList.remove("hidden");
  }

  function hideStatus() {
    statusEl.classList.add("hidden");
  }
})();
