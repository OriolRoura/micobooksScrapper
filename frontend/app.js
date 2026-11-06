const state = {
  historyRecords: [],
  historySource: "server",
  imageBlob: null,
  imageCapture: null,
  stream: null
};
const elements = {
  cameraCanvas: document.querySelector("[data-camera-canvas]"),
  cameraEmpty: document.querySelector("[data-camera-empty]"),
  cameraMessage: document.querySelector("[data-camera-message]"),
  cameraPreview: document.querySelector("[data-camera-preview]"),
  cameraStage: document.querySelector("[data-camera-stage]"),
  historyBackdrop: document.querySelector("[data-history-backdrop]"),
  historyClose: document.querySelector("[data-history-close]"),
  historyCount: document.querySelector("[data-history-count]"),
  historyDownload: document.querySelector("[data-history-download]"),
  historyDrawer: document.querySelector("[data-history-drawer]"),
  historyFile: document.querySelector("[data-history-file]"),
  historyList: document.querySelector("[data-history-list]"),
  historyOpen: document.querySelector("[data-history-open]"),
  historyRefresh: document.querySelector("[data-history-refresh]"),
  historySummary: document.querySelector("[data-history-summary]"),
  historySource: document.querySelector("[data-history-source]"),
  historyTotal: document.querySelector("[data-history-total]"),
  imageInput: document.querySelector("[data-image-input]"),
  imagePreview: document.querySelector("[data-image-preview]"),
  message: document.querySelector("[data-message]"),
  resultImage: document.querySelector("[data-result-image]"),
  resultIdentifiers: document.querySelector("[data-result-identifiers]"),
  resultPanel: document.querySelector("[data-result-panel]"),
  resultPrice: document.querySelector("[data-result-price]"),
  resultTitle: document.querySelector("[data-result-title]"),
  startCamera: document.querySelector("[data-start-camera]"),
  submitImage: document.querySelector("[data-submit-image]"),
  takePhoto: document.querySelector("[data-take-photo]")
};

function showMessage(text, isError = false) {
  elements.message.textContent = text;
  elements.message.classList.toggle("error", isError);
}

function setHistoryDrawer(open) {
  elements.historyDrawer.hidden = !open;
  elements.historyBackdrop.hidden = !open;
  elements.historyDrawer.setAttribute("aria-hidden", String(!open));
  document.body.classList.toggle("drawer-open", open);
}

function formatHistoryDate(value) {
  if (!value) return "Date unavailable";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

function createDecisionButton(record, decision, label) {
  const button = document.createElement("button");
  button.className = "decision-button";
  button.dataset.decision = decision;
  button.dataset.recordId = record.id;
  button.textContent = label;
  if (record.sell_decision === decision) button.classList.add("is-active");
  return button;
}

function renderHistory(records, sourceLabel) {
  state.historyRecords = records;
  elements.historyCount.textContent = String(records.length);
  const pricedCount = records.filter((record) => record.found).length;
  const sellCount = records.filter((record) => record.sell_decision === "sell").length;
  const sellTotal = records
    .filter((record) => record.sell_decision === "sell")
    .reduce((total, record) => total + (Number(record.seller_profit) || 0), 0);
  elements.historySummary.textContent = `${records.length} analyzed · ${pricedCount} with price · ${sellCount} marked sell`;
  elements.historyTotal.textContent = `Total for marked sell: ${sellTotal.toFixed(2)} EUR`;
  elements.historySource.textContent = sourceLabel;
  elements.historyList.replaceChildren();

  if (!records.length) {
    const empty = document.createElement("p");
    empty.className = "history-empty";
    empty.textContent = "No analyzed books yet.";
    elements.historyList.append(empty);
    return;
  }

  records.forEach((record) => {
    const item = document.createElement("article");
    item.className = `history-item ${record.found ? "is-found" : "is-missing"}`;

    const title = document.createElement("h3");
    title.textContent = record.title || (record.found ? "Title unavailable" : "No price found");
    item.append(title);

    const isbn = document.createElement("p");
    isbn.className = "history-isbn";
    isbn.textContent = `ISBN: ${record.isbn || "Unavailable"}`;
    item.append(isbn);

    const date = document.createElement("p");
    date.className = "history-meta";
    date.textContent = formatHistoryDate(record.analyzed_at);
    item.append(date);

    if (record.found) {
      const price = document.createElement("p");
      price.className = "history-price";
      price.textContent = `${Number(record.seller_profit).toFixed(2)} EUR`;
      item.append(price);

      const decisions = document.createElement("div");
      decisions.className = "decision-row";
      decisions.append(
        createDecisionButton(record, "sell", "Sell"),
        createDecisionButton(record, "not_sell", "Do not sell")
      );
      item.append(decisions);
    }

    elements.historyList.append(item);
  });
}

async function loadServerHistory() {
  elements.historySource.textContent = "Loading server history...";
  try {
    const response = await fetch("/api/history");
    const records = await response.json();
    if (!response.ok || !Array.isArray(records)) throw new Error("History could not be loaded.");
    state.historySource = "server";
    renderHistory(records, "Stored on this server");
  } catch (error) {
    elements.historySource.textContent = error.message;
    renderHistory([], "History unavailable");
  }
}

async function loadHistoryFile(event) {
  const [file] = event.target.files;
  if (!file) return;

  try {
    const records = JSON.parse(await file.text());
    if (!Array.isArray(records) || records.some((record) => !record || typeof record.isbn !== "string")) {
      throw new Error("The JSON must contain an array of records with ISBN values.");
    }
    state.historySource = "file";
    renderHistory(records, `Loaded locally from ${file.name}`);
  } catch (error) {
    elements.historySource.textContent = error.message;
  }
  event.target.value = "";
}

async function updateDecision(recordId, decision) {
  const record = state.historyRecords.find((item) => item.id === recordId);
  if (!record) return;

  try {
    if (state.historySource === "server") {
      const response = await fetch(`/api/history/${encodeURIComponent(recordId)}/decision`, {
        body: JSON.stringify({ decision }),
        headers: { "Content-Type": "application/json" },
        method: "PATCH"
      });
      const updated = await response.json();
      if (!response.ok) throw new Error(updated.detail || "Decision could not be saved.");
      Object.assign(record, updated);
    } else {
      record.sell_decision = decision;
    }
    renderHistory(state.historyRecords, state.historySource === "server" ? "Stored on this server" : elements.historySource.textContent);
  } catch (error) {
    elements.historySource.textContent = error.message;
  }
}

function downloadHistory() {
  const file = new Blob([JSON.stringify(state.historyRecords, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(file);
  const link = document.createElement("a");
  link.href = url;
  link.download = "analyzed_books.json";
  link.click();
  URL.revokeObjectURL(url);
}

function stopCamera() {
  if (state.stream) {
    state.stream.getTracks().forEach((track) => track.stop());
    state.stream = null;
  }
  elements.cameraPreview.hidden = true;
  elements.takePhoto.hidden = true;
  elements.startCamera.hidden = false;
}

async function openCamera() {
  console.info("[camera] Open camera clicked.");
  elements.cameraMessage.textContent = "Requesting camera permission...";
  showMessage("Requesting camera permission...", false);
  if (!navigator.mediaDevices?.getUserMedia) {
    console.error("[camera] navigator.mediaDevices.getUserMedia is unavailable.");
    elements.cameraMessage.textContent = "Camera is unavailable in this browser or page context.";
    showMessage("Camera API unavailable. Use Choose image or open the page from localhost/HTTPS.", true);
    return;
  }

  try {
    console.info("[camera] Requesting camera permission.");
    state.imageBlob = null;
    elements.imagePreview.hidden = true;
    elements.submitImage.hidden = true;
    state.stream = await navigator.mediaDevices.getUserMedia({
      audio: false,
      video: {
        facingMode: { ideal: "environment" },
        height: { ideal: 1080 },
        width: { ideal: 1920 }
      }
    });
    console.info("[camera] Camera permission granted and stream opened.");
    const [videoTrack] = state.stream.getVideoTracks();
    const cameraSettings = videoTrack.getSettings();
    if (cameraSettings.width && cameraSettings.height) {
      elements.cameraStage.style.aspectRatio = `${cameraSettings.width} / ${cameraSettings.height}`;
      console.info("[camera] Active resolution:", cameraSettings.width, "x", cameraSettings.height);
    }
    elements.cameraPreview.srcObject = state.stream;
    elements.cameraPreview.hidden = false;
    elements.cameraEmpty.hidden = true;
    elements.startCamera.hidden = true;
    state.imageCapture = null;
    if ("ImageCapture" in window) {
      try {
        state.imageCapture = new ImageCapture(videoTrack);
        console.info("[camera] Native still capture is available.");
      } catch (error) {
        console.warn("[camera] Native still capture unavailable; using video frame fallback.", error);
        elements.cameraMessage.textContent = "Live camera is ready. Using preview capture on this browser.";
      }
    }
    elements.takePhoto.hidden = false;
    elements.cameraMessage.textContent = "Frame the ISBN and take the photo.";
  } catch (error) {
    console.error("[camera] Camera startup failed.", error.name, error.message, error);
    elements.cameraMessage.textContent = "Camera could not be opened. Check browser permission or choose an image instead.";
    showMessage(`Camera failed (${error.name || "UnknownError"}): ${error.message || "No further details"}`, true);
  }
}

function setImagePreview(blob) {
  state.imageBlob = blob;
  elements.resultPanel.hidden = true;
  elements.imagePreview.src = URL.createObjectURL(blob);
  elements.imagePreview.hidden = false;
  elements.submitImage.hidden = false;
  elements.cameraEmpty.hidden = true;
  elements.cameraPreview.hidden = true;
  elements.cameraMessage.textContent = "Image ready. It will be sent for ISBN recognition.";
}

async function takePhoto() {
  console.info("[camera] Take photo clicked.");
  const { videoWidth, videoHeight } = elements.cameraPreview;
  if (!videoWidth || !videoHeight) {
    console.error("[camera] Video frame has no dimensions.");
    showMessage("Camera preview is not ready yet. Try again in a moment.", true);
    return;
  }
  if (state.imageCapture?.grabFrame) {
    try {
      const frame = await state.imageCapture.grabFrame();
      elements.cameraCanvas.width = frame.width;
      elements.cameraCanvas.height = frame.height;
      elements.cameraCanvas.getContext("2d").drawImage(frame, 0, 0);
      elements.cameraCanvas.toBlob((blob) => {
        if (blob) setImagePreview(blob);
        stopCamera();
      }, "image/jpeg", 0.95);
      console.info("[camera] Captured the visible camera frame.", frame.width, "x", frame.height);
      return;
    } catch (error) {
      console.warn("[camera] grabFrame failed; using video frame fallback.", error);
    }
  }
  if (!videoWidth || !videoHeight) {
    console.error("[camera] Video frame has no dimensions.");
    showMessage("Camera preview is not ready yet. Try again in a moment.", true);
    return;
  }
  elements.cameraCanvas.width = videoWidth;
  elements.cameraCanvas.height = videoHeight;
  elements.cameraCanvas.getContext("2d").drawImage(elements.cameraPreview, 0, 0);
  elements.cameraCanvas.toBlob((blob) => {
    if (blob) setImagePreview(blob);
    stopCamera();
  }, "image/jpeg", 0.9);
}

function renderResult(result) {
  elements.resultTitle.textContent = result.title;
  elements.resultIdentifiers.textContent = `ISBN: ${result.isbn || "-"}  /  EAN: ${result.ean || "-"}`;
  elements.resultPrice.textContent = `${Number(result.seller_profit).toFixed(2)} EUR`;
  if (result.image_url) {
    elements.resultImage.src = result.image_url;
    elements.resultImage.hidden = false;
  }
  elements.resultPanel.hidden = false;
}

async function requestQuote(isbn) {
  const searchedIsbn = String(isbn || "").trim();
  showMessage("Checking Micobooks...");
  try {
    const response = await fetch("/api/quote", {
      body: JSON.stringify({ isbn }),
      headers: { "Content-Type": "application/json" },
      method: "POST"
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "The quote could not be retrieved.");
    renderResult(payload);
    showMessage("Quote received.");
  } catch (error) {
    showMessage(`ISBN ${searchedIsbn}: ${error.message}`, true);
  }
}

async function submitImage() {
  if (!state.imageBlob) {
    showMessage("Choose or take an image first.", true);
    return;
  }
  const formData = new FormData();
  formData.append("image", state.imageBlob, "book.jpg");
  showMessage("Sending image for ISBN recognition...");
  try {
    const response = await fetch("/api/quote-from-image", { body: formData, method: "POST" });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "The image could not be analyzed.");
    renderResult(payload);
    showMessage("Quote received.");
  } catch (error) {
    showMessage(error.message, true);
  }
}

document.querySelector("[data-start-camera]").addEventListener("click", openCamera);
elements.takePhoto.addEventListener("click", takePhoto);
elements.submitImage.addEventListener("click", submitImage);
elements.historyOpen.addEventListener("click", () => {
  setHistoryDrawer(true);
  loadServerHistory();
});
elements.historyClose.addEventListener("click", () => setHistoryDrawer(false));
elements.historyBackdrop.addEventListener("click", () => setHistoryDrawer(false));
elements.historyRefresh.addEventListener("click", loadServerHistory);
elements.historyDownload.addEventListener("click", downloadHistory);
elements.historyFile.addEventListener("change", loadHistoryFile);
elements.historyList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-decision]");
  if (button) updateDecision(button.dataset.recordId, button.dataset.decision);
});
elements.imageInput.addEventListener("change", (event) => {
  const [file] = event.target.files;
  if (file) {
    stopCamera();
    setImagePreview(file);
  }
});

document.querySelector("[data-isbn-form]").addEventListener("submit", (event) => {
  event.preventDefault();
  requestQuote(new FormData(event.currentTarget).get("isbn"));
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") setHistoryDrawer(false);
});

loadServerHistory();
