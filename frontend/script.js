const $ = (id) => document.getElementById(id);

async function startDebate() {
  const topic = $("topic-input").value.trim();
  const numSolutions = parseInt($("num-solutions").value, 10) || 4;
  const numBatches = parseInt($("num-batches").value, 10) || 2;
  const roundsPerBatch = parseInt($("rounds-per-batch").value, 10) || 2;

  if (!topic) {
    $("status").textContent = "Please enter a clear topic.";
    return;
  }

  const btn = $("start-btn");
  btn.disabled = true;
  $("status").textContent =
    "Running deep research and multi-agent debate. This may take tens of seconds…";
  $("proposals").innerHTML = "";
  $("history").innerHTML = "";
  $("final-report").textContent = "";

  try {
    const payload = {
      topic,
      language: "en",
      config: {
        num_solutions: numSolutions,
        num_batches: numBatches,
        rounds_per_batch: roundsPerBatch,
      },
    };

    const res = await fetch("/api/debate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Backend responded with error status: ${res.status} - ${text}`);
    }

    const data = await res.json();
    renderResult(data.result);
    $("status").textContent =
      "Debate finished. You can tweak parameters and run again with a different configuration.";
  } catch (err) {
    console.error(err);
    $("status").textContent = `Request failed: ${err.message}`;
  } finally {
    btn.disabled = false;
  }
}

function renderResult(result) {
  renderProposals(result.proposals);
  renderHistory(result.history);
  $("final-report").textContent = result.final_report || "";
}

function renderProposals(proposals) {
  const container = $("proposals");
  if (!proposals || proposals.length === 0) {
    container.innerHTML = "<p class='hint'>No proposals generated yet.</p>";
    return;
  }

  container.innerHTML = "";
  for (const p of proposals) {
    const div = document.createElement("div");
    div.className = "proposal-card";
    div.innerHTML = `
      <div class="proposal-title">
        <span class="proposal-id">#${p.id}</span>
        &nbsp;${escapeHtml(p.name || "Untitled proposal")}
      </div>
      <div class="proposal-summary">
        ${escapeHtml(p.summary || "")}
      </div>
    `;
    container.appendChild(div);
  }
}

function renderHistory(history) {
  const container = $("history");
  if (!history || history.length === 0) {
    container.innerHTML = "<p class='hint'>No debate turns yet.</p>";
    return;
  }

  container.innerHTML = "";
  for (const h of history) {
    const div = document.createElement("div");
    div.className = "turn";
    const roleClass = h.role === "moderator" ? "turn-role moderator" : "turn-role";
    div.innerHTML = `
      <div class="turn-header">
        <div>
          <span class="${roleClass}">${h.role}</span>
          &nbsp;${escapeHtml(h.agent_name)}
        </div>
        <div>Batch ${h.batch} · Round ${h.round}</div>
      </div>
      <div class="turn-content">${escapeHtml(h.content || "")}</div>
    `;
    container.appendChild(div);
  }
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

window.addEventListener("DOMContentLoaded", () => {
  $("start-btn").addEventListener("click", startDebate);
});


