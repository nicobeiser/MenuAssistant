// metrics.js
console.log("metrics.js cargado");
console.count("metrics.js EVAL");

const API_BASE = "http://127.0.0.1:8000";

async function safeFetch(url, opts) {
  try {
    const r = await fetch(url, opts);
    if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
    return await r.json();
  } catch (e) {
    console.warn("fetch fail:", url, e);
    return null;
  }
}

function fmtMs(n) {
  return n === null || n === undefined ? "–" : `${Math.round(n)} ms`;
}
function fmtPct(r) {
  return r === null || r === undefined ? "–" : `${Math.round(r * 100)} %`;
}

function getEl(id) {
  const el = document.getElementById(id);
  if (!el) console.warn("Missing element:", id);
  return el;
}

async function loadSummary() {
  const elTotal = getEl("totalChats");
  const elAvgT = getEl("avgTotal");
  const elAvgM = getEl("avgModel");
  const elRatio = getEl("modelRatio");
  const elErr = getEl("totalErrors");

  if (!elTotal || !elAvgT || !elAvgM || !elRatio || !elErr) return;

  const data =
    (await safeFetch(`${API_BASE}/metrics/chat/summary?days=7`)) ||
    (await safeFetch(`${API_BASE}/metrics/summary?days=7`));

  if (!data) return;

  // backend actual
  elTotal.innerText = data.total_chats ?? "–";
  elAvgT.innerText = fmtMs(data.avg_total_ms ?? data.avg_latency_ms ?? data.avg_total);
  elAvgM.innerText = fmtMs(data.avg_model_ms ?? data.avg_model);

  const ratio =
    data.avg_model_ms && data.avg_total_ms ? data.avg_model_ms / data.avg_total_ms : null;

  elRatio.innerText = fmtPct(ratio);
  elErr.innerText = data.errors ?? 0;
}

let breakdownChart = null;
async function loadBreakdown() {
  if (!window.Chart) {
    console.warn("Chart.js no está cargado");
    return;
  }
  const canvas = document.getElementById("breakdownChart");
  if (!canvas) return;

  const data =
    (await safeFetch(`${API_BASE}/metrics/chat/breakdown?days=7`)) ||
    (await safeFetch(`${API_BASE}/metrics/breakdown?days=7`));

  if (!data) {
    console.warn("no breakdown data");
    return;
  }

  const labels = data.labels || ["preprocess", "model", "postprocess"];
  const values = data.values || [data.pre_ms || 0, data.model_ms || 0, data.post_ms || 0];

  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  if (breakdownChart) breakdownChart.destroy();
  breakdownChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels,
      datasets: [
        {
          data: values.map((v) => Math.round(v)),
          backgroundColor: [
            "rgba(14,160,106,0.95)",
            "rgba(212,175,55,0.95)",
            "rgba(60,120,80,0.90)",
          ],
          hoverOffset: 6,
          borderWidth: 1,
          borderColor: "rgba(0,0,0,0.35)",
        },
      ],
    },
    options: {
      plugins: {
        legend: { position: "bottom", labels: { color: "#dfebe1" } },
      },
    },
  });
}

let latencyTrendChart = null;
async function loadLatencyTrend() {
  if (!window.Chart) return;
  const canvas = document.getElementById("latencyTrend");
  if (!canvas) return;

  const data =
    (await safeFetch(`${API_BASE}/metrics/chat/latency-timeseries?days=30`)) ||
    (await safeFetch(`${API_BASE}/metrics/latency_timeseries?days=30`));

  if (!data) return;

  const labels = data.days || data.labels || [];
  const p50 = data.p50 || data.p50_ms || [];
  const p95 = data.p95 || data.p95_ms || [];

  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  if (latencyTrendChart) latencyTrendChart.destroy();
  latencyTrendChart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "p50 total",
          data: p50,
          borderColor: "#10b981",
          tension: 0.25,
          pointRadius: 2,
          fill: false,
        },
        {
          label: "p95 total",
          data: p95,
          borderColor: "#d4af37",
          tension: 0.25,
          pointRadius: 2,
          fill: false,
        },
      ],
    },
    options: {
      plugins: { legend: { labels: { color: "#dfebe1" } } },
      scales: {
        x: { ticks: { color: "#dfebe1" } },
        y: { ticks: { color: "#dfebe1" } },
      },
    },
  });
}

let dailyChart = null;
async function loadDaily() {
  if (!window.Chart) return;
  const canvas = document.getElementById("dailyChart");
  if (!canvas) return;

  const data = (await safeFetch(`${API_BASE}/metrics/daily`)) || [];
  if (!Array.isArray(data) || data.length === 0) return;

  const days = [...new Set(data.map((d) => d.day))].sort();
  const chats = days.map((day) => {
    const f = data.find((x) => x.day === day && x.type === "chat");
    return f ? f.count : 0;
  });
  const uploads = days.map((day) => {
    const f = data.find((x) => x.day === day && x.type === "upload");
    return f ? f.count : 0;
  });

  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  if (dailyChart) dailyChart.destroy();
  dailyChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: days,
      datasets: [
        {
          label: "Chats",
          data: chats,
          stack: "stack1",
          backgroundColor: "rgba(14,160,106,0.90)",
        },
        {
          label: "Uploads",
          data: uploads,
          stack: "stack1",
          backgroundColor: "rgba(212,175,55,0.90)",
        },
      ],
    },
    options: {
      plugins: { legend: { labels: { color: "#dfebe1" } } },
      scales: {
        x: { ticks: { color: "#dfebe1" } },
        y: { ticks: { color: "#dfebe1" } },
      },
      responsive: true,
    },
  });
}

async function loadRecent() {
  const tbody = document.querySelector("#recentTable tbody");
  if (!tbody) return;

  const data =
    (await safeFetch(`${API_BASE}/metrics/chat/recent?limit=25`)) ||
    (await safeFetch(`${API_BASE}/metrics/recent?limit=25`));

  tbody.innerHTML = "";
  if (!Array.isArray(data)) return;

  for (const r of data) {
    const tr = document.createElement("tr");
    const ts = r.ts || r.timestamp || r.time || "";
    const total = r.total_ms ?? r.duration_ms;
    tr.innerHTML = `
      <td>${ts}</td>
      <td>${r.request_id ?? r.id ?? "—"}</td>
      <td>${r.type ?? "—"}</td>
      <td>${total !== null && total !== undefined ? Math.round(total) : "—"}</td>
      <td>${r.model_ms !== null && r.model_ms !== undefined ? Math.round(r.model_ms) : "—"}</td>
      <td style="max-width:420px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${r.meta ?? ""}</td>
    `;
    tbody.appendChild(tr);
  }
}

// -------- polling robusto (1 solo) --------
let __refreshing = false;

async function refreshAll() {
  if (__refreshing) return;
  __refreshing = true;
  try {
    console.log("refreshAll", new Date().toLocaleTimeString());
    await Promise.allSettled([
      loadSummary(),
      loadBreakdown(),
      loadLatencyTrend(),
      loadDaily(),
      loadRecent(),
    ]);
  } finally {
    __refreshing = false;
  }
}

function startDashboardPolling() {
  // Evitar duplicados si Live Server reinyecta scripts
  if (window.__metricsInterval) return;

  refreshAll();
  window.__metricsInterval = setInterval(refreshAll, 15000);
}

// Arranque único
window.addEventListener("DOMContentLoaded", startDashboardPolling, { once: true });