const API_BASE = "http://127.0.0.1:8000";

async function loadSummary() {
  const res = await fetch(`${API_BASE}/metrics/summary`);
  const data = await res.json();

  document.getElementById("totalChats").innerText = data.total_chats;
  document.getElementById("avgLatency").innerText = Math.round(data.avg_latency_ms);
  document.getElementById("totalErrors").innerText = data.errors;
}

async function loadDailyChart() {
  const res = await fetch(`${API_BASE}/metrics/daily`);
  const data = await res.json();

  const days = [...new Set(data.map(d => d.day))];

  const chatCounts = days.map(day => {
    const found = data.find(d => d.day === day && d.type === "chat");
    return found ? found.count : 0;
  });

  const uploadCounts = days.map(day => {
    const found = data.find(d => d.day === day && d.type === "upload");
    return found ? found.count : 0;
  });

  const ctx = document.getElementById("dailyChart").getContext("2d");

  new Chart(ctx, {
    type: "line",
    data: {
      labels: days,
      datasets: [
        {
          label: "Chats",
          data: chatCounts,
          borderColor: "#3b82f6",
          backgroundColor: "rgba(59,130,246,0.2)",
          tension: 0.3
        },
        {
          label: "Uploads",
          data: uploadCounts,
          borderColor: "#10b981",
          backgroundColor: "rgba(16,185,129,0.2)",
          tension: 0.3
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          labels: { color: "white" }
        }
      },
      scales: {
        x: {
          ticks: { color: "white" }
        },
        y: {
          ticks: { color: "white" }
        }
      }
    }
  });
}

async function init() {
  await loadSummary();
  await loadDailyChart();
}

init();