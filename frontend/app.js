const state = { imageBlob: null, imageCapture: null, stream: null };
const elements = {
  cameraCanvas: document.querySelector("[data-camera-canvas]"),
  cameraEmpty: document.querySelector("[data-camera-empty]"),
  cameraMessage: document.querySelector("[data-camera-message]"),
  cameraPreview: document.querySelector("[data-camera-preview]"),
  cameraStage: document.querySelector("[data-camera-stage]"),
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
