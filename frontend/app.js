const watchlistEl = document.getElementById("watchlist");
const resultsSection = document.getElementById("results-section");
const resultsEl = document.getElementById("results");
const analyzeAllBtn = document.getElementById("analyze-all");
const addForm = document.getElementById("add-company-form");
const inputCompany = document.getElementById("input-company");
const inputLocation = document.getElementById("input-location");

let watchlist = [];

function renderWatchlist() {
  watchlistEl.innerHTML = watchlist
    .map(
      (c) => `
      <div class="company-chip">
        <span class="dot"></span>${c.company}
        <span class="remove" data-company="${c.company}" title="Remove">✕</span>
      </div>`
    )
    .join("");

  watchlistEl.querySelectorAll(".remove").forEach((btn) => {
    btn.addEventListener("click", () => {
      const name = btn.dataset.company;
      watchlist = watchlist.filter((e) => e.company !== name);
      renderWatchlist();
    });
  });
}

async function loadWatchlist() {
  const res = await fetch("/watchlist");
  watchlist = await res.json();
  renderWatchlist();
}

addForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const company = inputCompany.value.trim();
  const location = inputLocation.value.trim() || "United States";

  document.getElementById("add-error")?.remove();

  const res = await fetch("/watchlist", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ company, location }),
  });

  if (!res.ok) {
    const err = await res.json();
    const msg = document.createElement("p");
    msg.id = "add-error";
    msg.className = "add-error";
    msg.textContent = err.detail;
    addForm.after(msg);
    return;
  }

  watchlist = await res.json();
  renderWatchlist();
  inputCompany.value = "";
  inputLocation.value = "";
});

function createLoadingCard(company) {
  const card = document.createElement("div");
  card.className = "brief-card loading";
  card.id = `card-${company.replace(/\s+/g, "-")}`;
  card.innerHTML = `<div class="spinner"></div> Analyzing ${company}…`;
  return card;
}

function renderBrief(company, jobCount, brief) {
  const depts = brief.department_breakdown || {};
  const maxCount = Math.max(...Object.values(depts), 1);

  const deptRows = Object.entries(depts)
    .filter(([, v]) => v > 0)
    .sort(([, a], [, b]) => b - a)
    .map(
      ([label, count]) => `
      <div class="dept-row">
        <span class="dept-label">${label}</span>
        <div class="dept-bar-track">
          <div class="dept-bar-fill" style="width:${Math.round((count / maxCount) * 100)}%"></div>
        </div>
        <span class="dept-count">${count}</span>
      </div>`
    )
    .join("");

  const signals = (brief.signals || [])
    .map(
      (s) => `
      <div class="signal-item">
        <div class="signal-type">${s.type.replace(/_/g, " ")}</div>
        <div class="signal-desc">${s.description}</div>
        <div class="signal-evidence">${s.evidence}</div>
      </div>`
    )
    .join("");

  const roles = (brief.top_roles || [])
    .map((r) => `<span class="role-tag">${r}</span>`)
    .join("");

  return `
    <div class="brief-header">
      <div>
        <h3>${company}</h3>
        <div class="job-count">${jobCount} active postings</div>
      </div>
      <span class="confidence-badge ${brief.confidence}">${brief.confidence}</span>
    </div>
    <div class="signal-summary">${brief.signal_summary}</div>
    <div class="signals-list">${signals}</div>
    ${deptRows ? `<div class="dept-breakdown"><h4>Department Breakdown</h4><div class="dept-bars">${deptRows}</div></div>` : ""}
    ${roles ? `<div class="top-roles">${roles}</div>` : ""}
  `;
}

async function analyzeCompany(entry) {
  const cardId = `card-${entry.company.replace(/\s+/g, "-")}`;
  const card = document.getElementById(cardId);

  try {
    const res = await fetch("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ company: entry.company, location: entry.location || "United States" }),
    });

    if (!res.ok) {
      const err = await res.json();
      card.className = "brief-card error";
      card.textContent = `${entry.company}: ${err.detail}`;
      return;
    }

    const data = await res.json();
    card.className = "brief-card";
    card.innerHTML = renderBrief(entry.company, data.job_count, data.brief);
  } catch (err) {
    card.className = "brief-card error";
    card.textContent = `${entry.company}: ${err.message}`;
  }
}

analyzeAllBtn.addEventListener("click", async () => {
  // Auto-add any company typed but not yet submitted
  if (inputCompany.value.trim()) {
    await addForm.requestSubmit();
    // Small delay to let the DOM update
    await new Promise((r) => setTimeout(r, 50));
  }

  analyzeAllBtn.disabled = true;
  resultsEl.innerHTML = "";
  resultsSection.style.display = "block";

  for (const entry of watchlist) {
    resultsEl.appendChild(createLoadingCard(entry.company));
  }

  await Promise.all(watchlist.map(analyzeCompany));
  analyzeAllBtn.disabled = false;
});

loadWatchlist();
