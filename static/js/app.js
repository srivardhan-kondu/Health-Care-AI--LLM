/**
 * Accident Severity & Hospital Recommendation System
 * Frontend Logic — Upload, Geolocation, Analysis, Results Display
 * FR1.2–FR1.6, FR7.1–FR7.3, FR12.1–FR12.3
 */

(function () {
  "use strict";

  // ── State ──────────────────────────────────────────────────
  const state = {
    imageFile: null,
    imageFilename: null,
    analysisResult: null,
    location: { lat: null, lng: null, obtained: false },
  };

  // ── DOM refs ───────────────────────────────────────────────
  const uploadZone   = document.getElementById("uploadZone");
  const fileInput    = document.getElementById("fileInput");
  const imagePreview = document.getElementById("imagePreview");
  const analyzeBtn   = document.getElementById("analyzeBtn");
  const loadingOverlay  = document.getElementById("loadingOverlay");
  const loadingStep     = document.getElementById("loadingStep");
  const resultsSection  = document.getElementById("resultsSection");
  const errorToast      = document.getElementById("errorToast");
  const locationBadge   = document.getElementById("locationBadge");
  const locationText    = document.getElementById("locationText");

  // ── Init ───────────────────────────────────────────────────
  function init() {
    setupUploadZone();
    requestLocation(); // Prompt for location immediately on page load
    analyzeBtn.addEventListener("click", handleAnalyze);
  }

  // Call init on DOMContentLoaded to ensure geolocation is requested as soon as the page loads
  document.addEventListener("DOMContentLoaded", init);

  // ── Upload Zone ────────────────────────────────────────────
  function setupUploadZone() {
    uploadZone.addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (file) handleFile(file);
    });

    // Drag-and-drop
    ["dragenter", "dragover"].forEach((ev) => {
      uploadZone.addEventListener(ev, (e) => {
        e.preventDefault();
        uploadZone.classList.add("drag-over");
      });
    });

    ["dragleave", "drop"].forEach((ev) => {
      uploadZone.addEventListener(ev, (e) => {
        e.preventDefault();
        uploadZone.classList.remove("drag-over");
      });
    });

    uploadZone.addEventListener("drop", (e) => {
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    });
  }

  function handleFile(file) {
    const allowed = ["image/jpeg", "image/jpg", "image/png"];
    if (!allowed.includes(file.type)) {
      showError("❌ Unsupported format. Please upload a JPG, JPEG, or PNG image.");
      return;
    }

    state.imageFile = file;

    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.src = e.target.result;
      imagePreview.style.display = "block";
      uploadZone.classList.add("has-image");
      document.getElementById("uploadPlaceholder").style.display = "none";
      analyzeBtn.disabled = false;
    };
    reader.readAsDataURL(file);
  }

  // ── Geolocation ────────────────────────────────────────────
  function requestLocation() {
    if (!("geolocation" in navigator)) {
      setLocationText("⚠ Geolocation not supported");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        state.location.lat     = pos.coords.latitude;
        state.location.lng     = pos.coords.longitude;
        state.location.obtained = true;

        locationBadge.classList.add("has-location");
        locationText.textContent = `${state.location.lat.toFixed(4)}°, ${state.location.lng.toFixed(4)}°`;
      },
      () => {
        // Use Hyderabad default if denied
        state.location.lat     = 17.4435;
        state.location.lng     = 78.3772;
        state.location.obtained = true;
        setLocationText("📍 Using default location (Hyderabad)");
      },
      { timeout: 8000 }
    );
  }

  function setLocationText(text) {
    locationText.textContent = text;
  }

  // ── Analyze Flow ───────────────────────────────────────────
  async function handleAnalyze() {
    if (!state.imageFile) return;

    // Always request location before analysis
    await new Promise((resolve) => {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          state.location.lat = pos.coords.latitude;
          state.location.lng = pos.coords.longitude;
          state.location.obtained = true;
          locationBadge.classList.add("has-location");
          locationText.textContent = `${state.location.lat.toFixed(4)}°, ${state.location.lng.toFixed(4)}°`;
          resolve();
        },
        () => {
          // Use Hyderabad default if denied
          state.location.lat = 17.4435;
          state.location.lng = 78.3772;
          state.location.obtained = true;
          setLocationText("📍 Using default location (Hyderabad)");
          resolve();
        },
        { timeout: 8000 }
      );
    });

    showLoading("Uploading image…");
    hideResults();

    try {
      // Step 1 — Analyze image
      const analysisData = await uploadAndAnalyze();
      state.analysisResult = analysisData;
      state.imageFilename  = analysisData.image_filename;

      // Step 2 — Only fetch hospitals if injuries were detected
      let hospitals = [];
      if (analysisData.is_injured) {
        updateLoadingStep("Finding nearby hospitals…");
        const hospitalsData = await fetchHospitals(
          state.location.lat,
          state.location.lng,
          analysisData.primary_injury_type,
          analysisData.severity
        );
        hospitals = hospitalsData.hospitals;
      }

      hideLoading();
      renderResults(analysisData, hospitals);

    } catch (err) {
      hideLoading();
      hideResults(); // Ensure hospitals are hidden on error
      showError("Analysis stopped: " + (err.message || "Unknown error"));
    }
  }

  async function uploadAndAnalyze() {
    const formData = new FormData();
    formData.append("image", state.imageFile);

    const resp = await fetch("/analyze", { method: "POST", body: formData });

    const contentType = resp.headers.get("content-type") || "";
    if (!contentType.includes("application/json")) {
      throw new Error(`Server error (HTTP ${resp.status}). Please try again.`);
    }

    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || `HTTP ${resp.status}`);
    return data;
  }

  async function fetchHospitals(lat, lng, injuryType, severity) {
    const resp = await fetch("/hospitals", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lat, lng, injury_type: injuryType, severity }),
    });

    const contentType = resp.headers.get("content-type") || "";
    if (!contentType.includes("application/json")) {
      throw new Error(`Server error (HTTP ${resp.status}). Please try again.`);
    }

    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || `HTTP ${resp.status}`);
    return data;
  }

  // ── Render Results ─────────────────────────────────────────
  function renderResults(analysis, hospitals) {
    renderUploadedImage(analysis.image_filename);
    renderInjuryCard(analysis);

    // Hide hospital column if no injuries detected
    const hospitalCol = document.querySelector("#resultsSection .col-lg-7");
    if (analysis.is_injured) {
      hospitalCol.style.display = "";
      renderHospitals(hospitals);
    } else {
      hospitalCol.style.display = "none";
    }

    showResults();

    // Scroll to results
    setTimeout(() => {
      resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 100);
  }

  function renderUploadedImage(filename) {
    const img = document.getElementById("resultImage");
    img.src   = `/uploads/${filename}`;
    img.style.display = "block";
  }

  function renderInjuryCard(analysis) {
    // Demo banner
    const demoBanner = document.getElementById("demoBanner");
    demoBanner.style.display = analysis.demo_mode ? "flex" : "none";

    // Severity badge
    const sev = analysis.severity || "Moderate";
    const sevEl = document.getElementById("severityBadge");
    sevEl.className = `severity-badge ${sev}`;
    sevEl.innerHTML = `${severityIcon(sev)} ${sev}`;

    // Primary injury
    document.getElementById("primaryInjury").textContent = analysis.primary_injury_type || "Unknown";

    // Overall description
    document.getElementById("injuryDescription").textContent = analysis.overall_description || "";

    // Emergency flag
    const emerEl = document.getElementById("emergencyFlag");
    if (analysis.requires_emergency) {
      emerEl.innerHTML = `<span>🚨</span> Immediate emergency response required`;
      emerEl.style.display = "flex";
    } else {
      emerEl.style.display = "none";
    }

    // Confidence bar
    const confidence = Math.round((analysis.confidence || 0) * 100);
    document.getElementById("confidenceValue").textContent = `${confidence}%`;
    document.getElementById("confidenceFill").style.width   = `${confidence}%`;

    // Injury items list
    const listEl = document.getElementById("injuryList");
    listEl.innerHTML = "";
    (analysis.injuries || []).forEach((inj) => {
      listEl.innerHTML += `
        <div class="injury-item">
          <div class="injury-icon">${injuryEmoji(inj.type)}</div>
          <div>
            <div class="injury-type-name">${escHtml(inj.type)}</div>
            <div class="injury-desc">${escHtml(inj.description)}</div>
            ${inj.body_part ? `<span class="body-part-tag">📍 ${escHtml(inj.body_part)}</span>` : ""}
          </div>
        </div>`;
    });

    if (!analysis.injuries || analysis.injuries.length === 0) {
      listEl.innerHTML = `<p style="color:var(--text-muted); font-size:0.85rem;">No specific injuries detected.</p>`;
    }
  }

  function renderHospitals(hospitals) {
    const grid = document.getElementById("hospitalGrid");
    grid.innerHTML = "";

    hospitals.forEach((h, i) => {
      const rank    = i + 1;
      const rankCls = rank <= 3 ? `rank-${rank}` : "rank-other";
      const specCls = specClass(h.specialization);
      const dist    = h.distance_km ? `${h.distance_km} km` : "—";

      grid.innerHTML += `
        <div class="glass-card hospital-card">
          <div class="d-flex align-items-center gap-2 mb-2">
            <div class="hospital-rank ${rankCls}">#${rank}</div>
            <div class="hospital-name">${escHtml(h.name)}</div>
          </div>
          <span class="hospital-spec ${specCls}">${escHtml(h.specialization)}</span>
          <div class="hospital-meta">
            <div class="meta-item">
              <span>📏</span>
              <span class="distance-badge">${dist}</span>
            </div>
          </div>
          <span class="emergency-pill ${h.emergency ? "emergency-yes" : "emergency-no"}">
            ${h.emergency ? "🟢 Emergency Available" : "⚫ No Emergency"}
          </span>
        </div>`;
    });

    if (hospitals.length === 0) {
      grid.innerHTML = `<p style="color:var(--text-muted);">No hospitals found for this location.</p>`;
    }
  }

  // ── Helpers ────────────────────────────────────────────────
  function severityIcon(sev) {
    return { Severe: "🔴", Moderate: "🟠", Minor: "🟢" }[sev] || "⚪";
  }

  function injuryEmoji(type) {
    const t = (type || "").toLowerCase();
    if (t.includes("head") || t.includes("brain"))   return "🧠";
    if (t.includes("arm") || t.includes("hand"))     return "💪";
    if (t.includes("leg") || t.includes("knee"))     return "🦵";
    if (t.includes("bleed") || t.includes("blood"))  return "🩸";
    if (t.includes("fracture") || t.includes("bone")) return "🦴";
    if (t.includes("burn"))                           return "🔥";
    if (t.includes("chest") || t.includes("torso"))  return "🫁";
    return "🤕";
  }

  function specClass(spec) {
    if (!spec) return "spec-general";
    const s = spec.toLowerCase();
    if (s.includes("trauma"))    return "spec-trauma";
    if (s.includes("orthopedic") || s.includes("ortho")) return "spec-ortho";
    if (s.includes("emergency")) return "spec-emergency";
    if (s.includes("neurology")) return "spec-neurology";
    return "spec-general";
  }

  function escHtml(str) {
    const div = document.createElement("div");
    div.textContent = str || "";
    return div.innerHTML;
  }

  // ── UI State Toggles ───────────────────────────────────────
  function showLoading(step) {
    loadingStep.textContent = step;
    loadingOverlay.classList.add("active");
  }

  function updateLoadingStep(step) {
    loadingStep.textContent = step;
  }

  function hideLoading() {
    loadingOverlay.classList.remove("active");
  }

  function showResults() {
    resultsSection.classList.add("visible");
  }

  function hideResults() {
    resultsSection.classList.remove("visible");
  }

  function showError(msg) {
    errorToast.textContent = msg;
    errorToast.style.display = "block";
    setTimeout(() => { errorToast.style.display = "none"; }, 5000);
  }

  // ── Boot ───────────────────────────────────────────────────
  // Initialization is already bound at the top of the file
})();
