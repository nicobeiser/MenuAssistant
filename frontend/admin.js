const BASE_URL = "http://127.0.0.1:8000";

const $ = (id) => document.getElementById(id);

const dropzone = $("dropzone");
const fileInput = $("fileInput");
const imageGrid = $("imageGrid");
const noImages = $("noImages");
const imagesCount = $("imagesCount");
const uploadStatus = $("uploadStatus");
const uploadText = $("uploadText");
const btnDeleteAll = $("btnDeleteAll");

// --- Escape HTML ---
function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

// --- Upload ---
async function uploadFiles(files) {
  if (!files || files.length === 0) return;

  const form = new FormData();
  for (const f of files) form.append("files", f);

  uploadStatus.hidden = false;
  uploadText.textContent = `Uploading ${files.length} file(s)...`;

  try {
    const res = await fetch(`${BASE_URL}/upload`, { method: "POST", body: form });
    if (!res.ok) {
      const txt = await res.text();
      throw new Error(txt);
    }
    const data = await res.json();
    uploadText.textContent = `Uploaded: ${data.uploaded.join(", ")}`;
    setTimeout(() => { uploadStatus.hidden = true; }, 3000);
    refreshImages();
  } catch (err) {
    uploadText.textContent = "Upload failed. Is the backend running?";
    setTimeout(() => { uploadStatus.hidden = true; }, 4000);
    console.error(err);
  }
}

// --- File input ---
if (fileInput) {
  fileInput.addEventListener("change", () => {
    uploadFiles(fileInput.files);
    fileInput.value = "";
  });
}

// --- Drag & drop ---
if (dropzone) {
  ["dragenter", "dragover"].forEach((evt) => {
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach((evt) => {
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.remove("dragover");
    });
  });

  dropzone.addEventListener("drop", (e) => {
    const files = e.dataTransfer.files;
    uploadFiles(files);
  });
}

// --- Refresh image list ---
async function refreshImages() {
  try {
    const res = await fetch(`${BASE_URL}/images`);
    const data = await res.json();
    const images = data.images || [];

    imagesCount.textContent = `${images.length} image${images.length !== 1 ? "s" : ""}`;

    if (images.length === 0) {
      imageGrid.innerHTML = "";
      noImages.hidden = false;
      return;
    }

    noImages.hidden = true;
    imageGrid.innerHTML = images
      .map(
        (name) =>
          `<div class="image-card">
            <div class="image-preview">
              <img src="${BASE_URL}/images/${encodeURIComponent(name)}/file" alt="${escapeHtml(name)}"
                   onerror="this.parentElement.innerHTML='<span class=\\'preview-icon\\'>🖼</span>'" />
            </div>
            <div class="image-info">
              <span class="image-name" title="${escapeHtml(name)}">${escapeHtml(name)}</span>
              <button class="btn btn-danger btn-xs chip-del" data-name="${escapeHtml(name)}" title="Delete">&times;</button>
            </div>
          </div>`
      )
      .join("");

    imageGrid.querySelectorAll(".chip-del").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const name = btn.dataset.name;
        await fetch(`${BASE_URL}/images/${encodeURIComponent(name)}`, { method: "DELETE" });
        refreshImages();
      });
    });
  } catch (err) {
    console.error("Failed to load images", err);
    noImages.hidden = false;
    noImages.textContent = "Could not connect to backend.";
  }
}

// --- Delete all ---
if (btnDeleteAll) {
  btnDeleteAll.addEventListener("click", async () => {
    if (!confirm("Delete all menu images?")) return;
    try {
      await fetch(`${BASE_URL}/images`, { method: "DELETE" });
      refreshImages();
    } catch (err) {
      console.error(err);
    }
  });
}

// --- Init ---
refreshImages();
