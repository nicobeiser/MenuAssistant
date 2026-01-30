const API_URL = "http://localhost:8000/chat";

const $ = (id) => document.getElementById(id);

const messagesEl = $("messages");
const formEl = $("form");
const inputEl = $("input");
const btnClear = $("btnClear");
const dot = $("dot");
const statusText = $("statusText");

function setStatus(state, text) {
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

function escapeHtml(s) {
  return s
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

// Convierte **texto** a <strong>texto</strong> (seguro)
function renderMarkdownLite(text) {
  let html = escapeHtml(text);

  // **bold**
  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

  // bullets tipo "*   item"
  // Convierte líneas que empiezan con "*" en <li>
  const lines = html.split("\n");
  let inList = false;
  let out = [];

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
      // salto de línea normal
      out.push(line === "" ? "<br/>" : `<p>${line}</p>`);
    }
  }
  if (inList) out.push("</ul>");

  // Limpia <p><br/></p> raros si querés (opcional)
  return out.join("");
}

function addBubble(role, text) {
  const div = document.createElement("div");
  div.className = `bubble ${role}`;

  // Render bonito: bold + listas
  div.innerHTML = `<div class="msg">${renderMarkdownLite(text)}</div>`;

  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}


function loadHistory() {
  const raw = localStorage.getItem("chat_history");
  if (!raw) return;
  try {
    const history = JSON.parse(raw);
    history.forEach((m) => addBubble(m.role, m.text));
  } catch {}
}

function saveMessage(role, text) {
  const raw = localStorage.getItem("chat_history");
  const history = raw ? JSON.parse(raw) : [];
  history.push({ role, text });
  localStorage.setItem("chat_history", JSON.stringify(history.slice(-80)));
}

btnClear.addEventListener("click", () => {
  localStorage.removeItem("chat_history");
  messagesEl.innerHTML = "";
  addBubble("ai", "Listo. Borré la conversación.");
});

formEl.addEventListener("submit", async (e) => {
  e.preventDefault();

  const msg = inputEl.value.trim();
  if (!msg) return;

  inputEl.value = "";
  addBubble("user", msg);
  saveMessage("user", msg);

  setStatus("loading", "Pensando...");

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
    const reply = data.reply ?? "(sin reply)";
    addBubble("ai", reply);
    saveMessage("ai", reply);

    setStatus("ready", "Listo");
  } catch (err) {
    addBubble("ai", "Error conectando con el backend. Revisá que esté corriendo en http://localhost:8000");
    setStatus("error", "Error");
    console.error(err);
  }
});

loadHistory();
addBubble("ai", "Hola. Mandame un mensaje y lo mando al backend.");
setStatus("ready", "Listo");
