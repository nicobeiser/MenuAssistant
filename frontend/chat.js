const BASE_URL = "http://127.0.0.1:8000";
const API_URL = `${BASE_URL}/chat`;




const $ = (id) => document.getElementById(id);

const messagesEl = $("messages");
const formEl = $("form");
const inputEl = $("input");

const dot = $("dot");
const statusText = $("statusText");

// --- Estado UI ---
function setStatus(state, text) {
  if (!dot || !statusText) return;

  // state: "ready" | "loading" | "error"
  if (state === "ready") {
    dot.style.background = "#3ddc97";
    dot.style.boxShadow = "0 0 0 3px rgba(61,220,151,.15)";
  } else if (state === "loading") {
    dot.style.background = "#fbbf24";
    dot.style.boxShadow = "0 0 0 3px rgba(251,191,36,.15)";
  } else {
    dot.style.background = "#ff4d6d";
    dot.style.boxShadow = "0 0 0 3px rgba(255,77,109,.15)";
  }
  statusText.textContent = text;
}

// --- Seguridad HTML ---
function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

// Convierte **texto** a <strong>texto</strong> y listas tipo "* item"
function renderMarkdownLite(text) {
  let html = escapeHtml(text);

  // **bold**
  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

  const lines = html.split("\n");
  let inList = false;
  const out = [];

  for (const line of lines) {
    const m = line.match(/^\s*\*\s+(.*)$/);
    if (m) {
      if (!inList) {
        out.push("<ul>");
        inList = true;
      }
      out.push(`<li>${m[1]}</li>`);
    } else {
      if (inList) {
        out.push("</ul>");
        inList = false;
      }
      out.push(line === "" ? "<br/>" : `<p>${line}</p>`);
    }
  }
  if (inList) out.push("</ul>");

  return out.join("");
}

function addBubble(role, text) {
  if (!messagesEl) return;

  const div = document.createElement("div");
  div.className = `bubble ${role}`;
  div.innerHTML = `<div class="msg">${renderMarkdownLite(text)}</div>`;

  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function loadHistory() {
  const raw = localStorage.getItem("chat_history");
  if (!raw) return;

  try {
    const history = JSON.parse(raw);
    if (Array.isArray(history)) {
      history.forEach((m) => addBubble(m.role, m.text));
    }
  } catch {
    // si el JSON está corrupto, lo ignoramos
  }
}

function saveMessage(role, text) {
  const raw = localStorage.getItem("chat_history");
  let history = [];
  try {
    history = raw ? JSON.parse(raw) : [];
    if (!Array.isArray(history)) history = [];
  } catch {
    history = [];
  }

  history.push({ role, text });
  localStorage.setItem("chat_history", JSON.stringify(history.slice(-80)));
}

// --- Botón Clear (opcional) ---
const btnClear = $("btnClear");
if (btnClear) {
  btnClear.addEventListener("click", () => {
    localStorage.removeItem("chat_history");
    if (messagesEl) messagesEl.innerHTML = "";
    addBubble("ai", "Conversation deleted.");
  });
}

// --- Submit ---
if (formEl) {
  formEl.addEventListener("submit", async (e) => {
    e.preventDefault();

    const msg = (inputEl?.value ?? "").trim();
    if (!msg) return;

    if (inputEl) inputEl.value = "";

    addBubble("user", msg);
    saveMessage("user", msg);

    setStatus("loading", "Thinking...");

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg }),
      });

      if (!res.ok) {
        const txt = await res.text();
        throw new Error(`HTTP ${res.status}: ${txt}`);
      }

      const data = await res.json();
      const reply = data.reply ?? "(no reply)";

      addBubble("ai", reply);
      saveMessage("ai", reply);

      setStatus("ready", "Ready");
    } catch (err) {
      addBubble(
        "ai",
        "Error connecting to the backend. Make sure it is running at http://localhost:8000"
      );
      setStatus("error", "Error");
      console.error(err);
    }
  });
}

// --- Image Upload ---
const fileInput = $("fileInput");
const imageListEl = $("imageList");
const uploadZone = $("uploadZone");

async function refreshImages() {
  try {
    const res = await fetch(`${BASE_URL}/images`);
    const data = await res.json();
    if (!imageListEl) return;
    if (data.images.length === 0) {
      imageListEl.innerHTML = '<span class="no-images">No images uploaded yet.</span>';
      return;
    }
    imageListEl.innerHTML = data.images
      .map(
        (name) =>
          `<div class="image-chip">
            <span class="image-name">${escapeHtml(name)}</span>
            <button class="chip-del" data-name="${escapeHtml(name)}" title="Delete">&times;</button>
          </div>`
      )
      .join("");

    imageListEl.querySelectorAll(".chip-del").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const name = btn.dataset.name;
        await fetch(`${BASE_URL}/images/${encodeURIComponent(name)}`, { method: "DELETE" });
        refreshImages();
      });
    });
  } catch (err) {
    console.error("Failed to load images", err);
  }
}

if (fileInput) {
  fileInput.addEventListener("change", async () => {
    const files = fileInput.files;
    if (!files || files.length === 0) return;

    const form = new FormData();
    for (const f of files) form.append("files", f);

    setStatus("loading", "Uploading...");
    try {
      const res = await fetch(`${BASE_URL}/upload`, { method: "POST", body: form });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(txt);
      }
      const data = await res.json();
      addBubble("ai", `Uploaded ${data.uploaded.length} image(s): ${data.uploaded.join(", ")}`);
      setStatus("ready", "Ready");
      refreshImages();
    } catch (err) {
      addBubble("ai", "Error uploading images.");
      setStatus("error", "Upload error");
      console.error(err);
    }
    fileInput.value = "";
  });
}

// --- Init ---
loadHistory();
addBubble("ai", "Hello! Upload your menu images and ask me for recommendations.");
setStatus("ready", "Ready");
refreshImages();
