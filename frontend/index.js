/* ════════════════════════════════════════════════════════════════════
   FRIDAY v2 — App Logic
   ════════════════════════════════════════════════════════════════════ */

const API = "http://127.0.0.1:5000";

// ── State ─────────────────────────────────────────────────────────────────────
const state = {
  token:         localStorage.getItem("token") || "",
  name:          localStorage.getItem("name")  || "",
  username:      localStorage.getItem("username") || "",
  model:         localStorage.getItem("model") || "",
  mode:          "rag",            // "rag" | "search"
  groups:        [],               // all user groups
  activeGroups:  new Set(),        // group ids selected for context
  scannedFiles:  [],               // files from last scan
  selectedFiles: new Set(),        // file paths checked for indexing
  newGroupColor: "#6c72ff",
  panelOpen:     false,
};

const COLORS = [
  "#6c72ff","#3ecf6c","#f5a623","#ef4444","#a855f7",
  "#06b6d4","#f97316","#84cc16","#ec4899","#14b8a6",
];

// ── Auth guard ────────────────────────────────────────────────────────────────
(async () => {
  if (!state.token) { window.location.href = "login.html"; return; }
  try {
    const r = await apiFetch("/api/auth/me");
    if (!r.ok) throw new Error();
    const d = await r.json();
    state.name     = d.name;
    state.username = d.username;
    localStorage.setItem("name",     d.name);
    localStorage.setItem("username", d.username);
  } catch {
    window.location.href = "login.html";
    return;
  }
  initApp();
})();

// ── Init ──────────────────────────────────────────────────────────────────────
function initApp() {
  renderUserInfo();
  renderWelcome();
  initInput();
  loadModels();
  loadGroups();
  checkOllama();
  initColorSwatches("colorSwatches", false);
  initColorSwatches("modalColorSwatches", true);
}

function apiFetch(path, opts = {}) {
  return fetch(API + path, {
    ...opts,
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${state.token}`,
      ...(opts.headers || {}),
    },
  });
}

// ── User UI ───────────────────────────────────────────────────────────────────
function renderUserInfo() {
  const initial = (state.name || state.username || "?")[0].toUpperCase();
  document.getElementById("avatarEl").textContent   = initial;
  document.getElementById("userNameEl").textContent = state.name || state.username;
}

function renderWelcome() {
  const hour = new Date().getHours();
  const greet = hour < 12 ? "morning" : hour < 17 ? "afternoon" : "evening";
  document.getElementById("timeOfDay").textContent  = greet;
  document.getElementById("welcomeName").textContent = state.name || state.username;
}

async function logout() {
  try { await apiFetch("/api/auth/logout", { method: "POST" }); } catch {}
  localStorage.clear();
  window.location.href = "login.html";
}

// ── Ollama status ─────────────────────────────────────────────────────────────
async function checkOllama() {
  const dot = document.getElementById("ollamaStatus");
  try {
    const r = await apiFetch("/api/health");
    const d = await r.json();
    dot.className = "status-dot " + (d.ollama ? "online" : "offline");
    dot.title = d.ollama ? `Ollama online · ${d.models} model(s)` : "Ollama offline";
  } catch {
    dot.className = "status-dot offline";
  }
}

// ── Model selector ────────────────────────────────────────────────────────────
async function loadModels() {
  const r = await apiFetch("/api/models");
  const d = await r.json();
  const menu = document.getElementById("modelMenu");
  const icon = document.getElementById("modelIcon");

  if (!d.ollama_running || !d.models.length) {
    icon.className = "model-icon offline";
    document.getElementById("selectedModelName").textContent = "Ollama offline";
    menu.innerHTML = `<div class="model-offline-msg">Start Ollama to use local models</div>`;
    return;
  }

  icon.className = "model-icon";

  // pick saved model or first available
  if (!state.model || !d.models.find(m => m.name === state.model)) {
    state.model = pickDefaultModel(d.models);
    localStorage.setItem("model", state.model);
  } else if (state.model === "gemma3:1b" && d.models.find(m => m.name === "gemma3:270m")) {
    state.model = "gemma3:270m";
    localStorage.setItem("model", state.model);
  }
  updateModelDisplay(state.model);

  menu.innerHTML = "";
  d.models.forEach(m => {
    const el = document.createElement("div");
    el.className = "model-item" + (m.name === state.model ? " active" : "");
    const sizeMB = m.size ? (m.size / 1e9).toFixed(1) + " GB" : "";
    el.innerHTML = `<span class="model-item-name">${esc(m.name)}</span><span class="model-item-size">${sizeMB}</span>`;
    el.onclick = (e) => { e.stopPropagation(); selectModel(m.name); };
    menu.appendChild(el);
  });
}

function updateModelDisplay(name) {
  document.getElementById("selectedModelName").textContent = name;
}

function selectModel(name) {
  state.model = name;
  localStorage.setItem("model", name);
  updateModelDisplay(name);
  document.getElementById("modelMenu").classList.remove("open");
  document.getElementById("modelSelector").classList.remove("open");
  // refresh active marks
  document.querySelectorAll(".model-item").forEach(el => {
    el.classList.toggle("active", el.querySelector(".model-item-name")?.textContent === name);
  });
}

function pickDefaultModel(models) {
  return models.find(m => m.name === "gemma3:270m")?.name || models[0].name;
}

function toggleModelMenu() {
  const menu = document.getElementById("modelMenu");
  const sel  = document.getElementById("modelSelector");
  const isOpen = menu.classList.contains("open");
  menu.classList.toggle("open", !isOpen);
  sel.classList.toggle("open", !isOpen);
  if (!isOpen) {
    // close on outside click
    setTimeout(() => document.addEventListener("click", closeModelMenu, { once: true }), 0);
  }
}
function closeModelMenu() {
  document.getElementById("modelMenu")?.classList.remove("open");
  document.getElementById("modelSelector")?.classList.remove("open");
}

// ── Groups ────────────────────────────────────────────────────────────────────
async function loadGroups() {
  const r = await apiFetch("/api/groups");
  const d = await r.json();
  state.groups = d.groups || [];
  renderGroupList();
  renderPanelGroups();
  populateGroupSelect();
}

function renderGroupList() {
  const el = document.getElementById("groupList");
  if (!state.groups.length) {
    el.innerHTML = `<div class="empty-state">No databases yet<br><small>Open Database panel to create one</small></div>`;
    return;
  }
  el.innerHTML = "";
  state.groups.forEach(g => {
    const active = state.activeGroups.has(g.id);
    const div = document.createElement("div");
    div.className = "group-item" + (active ? " active" : "");
    div.dataset.gid = g.id;
    div.innerHTML = `
      <div class="group-dot" style="background:${esc(g.color)}"></div>
      <span class="group-name">${esc(g.name)}</span>
      <span class="group-count">${g.file_count}</span>`;
    div.onclick = () => toggleGroupContext(g.id);
    el.appendChild(div);
  });
  renderContextChips();
}

function toggleGroupContext(gid) {
  if (state.activeGroups.has(gid)) {
    state.activeGroups.delete(gid);
  } else {
    state.activeGroups.add(gid);
  }
  renderGroupList();
  renderContextChips();
  updateContextSummary();
}

function renderContextChips() {
  const el = document.getElementById("contextChips");
  el.innerHTML = "";
  state.activeGroups.forEach(gid => {
    const g = state.groups.find(x => x.id === gid);
    if (!g) return;
    const chip = document.createElement("div");
    chip.className = "ctx-chip";
    chip.style.cssText = `background:${hexAlpha(g.color,0.12)};border-color:${hexAlpha(g.color,0.3)};color:${g.color}`;
    chip.innerHTML = `
      <span class="ctx-chip-dot" style="background:${esc(g.color)}"></span>
      ${esc(g.name)}
      <span class="ctx-chip-x" onclick="toggleGroupContext(${gid})">×</span>`;
    el.appendChild(chip);
  });
}

function updateContextSummary() {
  const el = document.getElementById("contextSummary");
  if (!state.activeGroups.size) {
    el.textContent = "No context selected";
    return;
  }
  const names = [...state.activeGroups].map(id => state.groups.find(g => g.id === id)?.name).filter(Boolean);
  el.textContent = `Context: ${names.join(", ")}`;
}

function renderPanelGroups() {
  const el = document.getElementById("panelGroups");
  if (!state.groups.length) {
    el.innerHTML = `<div class="empty-state" style="padding:8px 0">No databases yet</div>`;
    return;
  }
  el.innerHTML = "";
  state.groups.forEach(g => {
    const div = document.createElement("div");
    div.className = "panel-group-item";
    div.innerHTML = `
      <div class="pgi-dot" style="background:${esc(g.color)}"></div>
      <div class="pgi-info">
        <div class="pgi-name">${esc(g.name)}</div>
        <div class="pgi-meta">${g.file_count} files · ${g.chunk_count} chunks</div>
      </div>
      <button class="pgi-del" onclick="deleteGroup(${g.id})" title="Delete">
        <svg viewBox="0 0 16 16" fill="none"><path d="M5 3h6M3 5h10M6 5v7M10 5v7M4 5l1 8h6l1-8" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </button>`;
    el.appendChild(div);
  });
}

function populateGroupSelect() {
  const sel = document.getElementById("groupSelect");
  sel.innerHTML = `<option value="">— Create new group —</option>`;
  state.groups.forEach(g => {
    const opt = document.createElement("option");
    opt.value = g.id;
    opt.textContent = g.name;
    sel.appendChild(opt);
  });
  sel.onchange = () => {
    document.getElementById("newGroupForm").style.display = sel.value ? "none" : "";
  };
}

async function deleteGroup(gid) {
  if (!confirm("Delete this database and all its indexed data?")) return;
  const r = await apiFetch(`/api/groups/${gid}`, { method: "DELETE" });
  if (r.ok) {
    state.activeGroups.delete(gid);
    await loadGroups();
    renderContextChips();
    updateContextSummary();
    toast("Database deleted", "success");
  } else {
    toast("Failed to delete", "error");
  }
}

// Modal for new group from sidebar
function openNewGroup() {
  document.getElementById("modalGroupName").value = "";
  document.getElementById("modal").classList.add("open");
  document.getElementById("modalBackdrop").classList.add("open");
  setTimeout(() => document.getElementById("modalGroupName").focus(), 50);
}
function closeModal() {
  document.getElementById("modal").classList.remove("open");
  document.getElementById("modalBackdrop").classList.remove("open");
}
async function createGroup() {
  const name  = document.getElementById("modalGroupName").value.trim();
  const color = document.querySelector("#modalColorSwatches .selected")?.dataset.color || "#6c72ff";
  if (!name) { toast("Enter a group name", "error"); return; }
  const r = await apiFetch("/api/groups", {
    method: "POST",
    body: JSON.stringify({ name, color }),
  });
  if (r.ok) {
    closeModal();
    await loadGroups();
    toast(`"${name}" created`, "success");
  } else {
    toast("Failed to create group", "error");
  }
}

// ── DB Panel ──────────────────────────────────────────────────────────────────
function openDbPanel() {
  state.panelOpen = true;
  document.getElementById("dbPanel").classList.add("open");
  document.getElementById("panelBackdrop").classList.add("open");
}
function closeDbPanel() {
  state.panelOpen = false;
  document.getElementById("dbPanel").classList.remove("open");
  document.getElementById("panelBackdrop").classList.remove("open");
}

// ── Color swatches ────────────────────────────────────────────────────────────
function initColorSwatches(containerId, isModal) {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = "";
  COLORS.forEach((c, i) => {
    const sw = document.createElement("div");
    sw.className = "color-swatch" + (i === 0 ? " selected" : "");
    sw.style.background = c;
    sw.dataset.color = c;
    sw.onclick = () => {
      el.querySelectorAll(".color-swatch").forEach(s => s.classList.remove("selected"));
      sw.classList.add("selected");
      if (!isModal) state.newGroupColor = c;
    };
    el.appendChild(sw);
  });
}

// ── Scan folder ───────────────────────────────────────────────────────────────
async function scanFolder() {
  const folder = document.getElementById("folderInput").value.trim();
  const hint   = document.getElementById("scanHint");
  const btn    = document.getElementById("scanBtn");
  if (!folder) { hint.textContent = "Enter a path first."; hint.className = "scan-hint error"; return; }

  hint.textContent = "Scanning…"; hint.className = "scan-hint";
  btn.disabled = true;
  btn.innerHTML = `<span class="spin"></span>Scan`;

  try {
    const r = await apiFetch("/api/scan", { method: "POST", body: JSON.stringify({ folder_path: folder }) });
    const d = await r.json();
    if (!r.ok) { hint.textContent = d.error; hint.className = "scan-hint error"; return; }

    state.scannedFiles = d.files;
    state.selectedFiles = new Set(d.files.map(f => f.file_path));

    hint.textContent = `Found ${d.count} PDF${d.count !== 1 ? "s" : ""}`;
    hint.className = "scan-hint ok";

    renderFileList();
    document.getElementById("scannedSection").style.display = d.count ? "" : "none";
    document.getElementById("indexSection").style.display   = d.count ? "" : "none";
  } catch (e) {
    hint.textContent = "Cannot reach backend.";
    hint.className = "scan-hint error";
  } finally {
    btn.disabled = false;
    btn.textContent = "Scan";
  }
}

function renderFileList() {
  const el = document.getElementById("fileList");
  el.innerHTML = "";
  state.scannedFiles.forEach(f => {
    const row = document.createElement("div");
    row.className = "file-row";
    row.innerHTML = `
      <input type="checkbox" data-path="${esc(f.file_path)}" checked
             onchange="onFileCheck(this)"/>
      <span class="file-row-name" title="${esc(f.file_path)}">${esc(f.file)}</span>
      <span class="file-row-size">${f.size_kb} KB</span>`;
    el.appendChild(row);
  });
}

function toggleSelectAll(cb) {
  document.querySelectorAll("#fileList input[type='checkbox']").forEach(box => {
    box.checked = cb.checked;
    if (cb.checked) state.selectedFiles.add(box.dataset.path);
    else            state.selectedFiles.delete(box.dataset.path);
  });
}
function onFileCheck(cb) {
  if (cb.checked) state.selectedFiles.add(cb.dataset.path);
  else            state.selectedFiles.delete(cb.dataset.path);
}

// ── Index ─────────────────────────────────────────────────────────────────────
async function indexSelected() {
  const paths = [...state.selectedFiles];
  if (!paths.length) { toast("Select at least one file", "error"); return; }

  // Determine group
  const sel   = document.getElementById("groupSelect");
  let groupId = parseInt(sel.value) || null;

  if (!groupId) {
    // Create new group
    const name  = document.getElementById("newGroupName").value.trim();
    const color = document.querySelector("#colorSwatches .selected")?.dataset.color || "#6c72ff";
    if (!name) { toast("Enter a group name", "error"); return; }
    const cr = await apiFetch("/api/groups", { method: "POST", body: JSON.stringify({ name, color }) });
    if (!cr.ok) { toast("Failed to create group", "error"); return; }
    const cd = await cr.json();
    groupId = cd.id;
    await loadGroups();
  }

  // Start indexing
  const btn = document.getElementById("indexBtn");
  btn.disabled = true; btn.innerHTML = `<span class="spin"></span>Indexing…`;

  const wrap  = document.getElementById("progressWrap");
  const bar   = document.getElementById("progressBar");
  const label = document.getElementById("progressLabel");
  wrap.style.display = "block";
  bar.style.width = "0%";
  label.textContent = "Starting…";

  try {
    const r = await fetch(API + "/api/index", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${state.token}` },
      body: JSON.stringify({ file_paths: paths, group_id: groupId }),
    });
    const reader  = r.body.getReader();
    const decoder = new TextDecoder();
    let buf = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      const lines = buf.split("\n"); buf = lines.pop();
      for (const line of lines) {
        if (!line.trim()) continue;
        try {
          const ev = JSON.parse(line);
          if (ev.type === "progress") {
            const pct = Math.round((ev.done / ev.total) * 100);
            bar.style.width  = pct + "%";
            label.textContent = `${ev.done}/${ev.total} — ${ev.file} (${ev.chunks} chunks)`;
          } else if (ev.type === "complete") {
            bar.style.width   = "100%";
            label.textContent = `Done! ${ev.indexed} indexed, ${ev.skipped} skipped`;
            toast(`Indexed ${ev.indexed} files`, "success");
            await loadGroups();
            setTimeout(() => { wrap.style.display = "none"; }, 3000);
          } else if (ev.type === "error") {
            toast(`Error: ${ev.error}`, "error");
          }
        } catch {}
      }
    }
  } catch (e) {
    toast("Indexing failed: " + e.message, "error");
  } finally {
    btn.disabled = false;
    btn.textContent = "Index selected files";
  }
}

// ── Mode ──────────────────────────────────────────────────────────────────────
function setMode(m) {
  state.mode = m;
  document.getElementById("modeRag").classList.toggle("active",    m === "rag");
  document.getElementById("modeSearch").classList.toggle("active", m === "search");
  document.getElementById("userInput").dataset.placeholder = m === "rag"
    ? "Ask anything…"
    : "Search a concept or topic…";
}

// ── Sidebar toggle ─────────────────────────────────────────────────────────────
function toggleSidebar() {
  document.getElementById("sidebar").classList.toggle("collapsed");
}

// ── Input ─────────────────────────────────────────────────────────────────────
function initInput() {
  const inp = document.getElementById("userInput");
  inp.addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); }
  });
}

function quickPrompt(text) {
  const inp = document.getElementById("userInput");
  inp.textContent = text;
  inp.focus();
}

function handleSend() {
  const inp  = document.getElementById("userInput");
  const text = inp.innerText.trim();
  if (!text) return;
  inp.textContent = "";

  // Hide welcome
  const welcome = document.getElementById("welcomeScreen");
  if (welcome) { welcome.style.display = "none"; }

  if (state.mode === "search") doSearch(text);
  else                         doRag(text);
}

// ── RAG Chat ──────────────────────────────────────────────────────────────────
async function doRag(message) {
  appendUserMsg(message);

  if (!state.model) { appendAiMsg("No model selected. Open the model selector in the sidebar."); return; }

  const aiRow  = appendAiMsgStreaming();
  const body   = aiRow.querySelector(".msg-body");
  const cursor = aiRow.querySelector(".cursor-blink");
  let   full   = "";

  try {
    const r = await fetch(API + "/api/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${state.token}` },
      body: JSON.stringify({
        message,
        model: state.model,
        group_ids: [...state.activeGroups],
      }),
    });

    if (!r.ok) {
      let detail = `Chat failed with HTTP ${r.status}`;
      try {
        const d = await r.json();
        if (d.error) detail = d.error;
      } catch {}
      throw new Error(detail);
    }
    if (!r.body) throw new Error("Chat stream did not open.");

    const reader  = r.body.getReader();
    const decoder = new TextDecoder();
    let   buf     = "";
    let   ctxUsed = 0;
    let   streamErrored = false;

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      const lines = buf.split("\n"); buf = lines.pop();

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        try {
          const ev = JSON.parse(line.slice(6));
          if (ev.type === "start") {
            ctxUsed = ev.context_chunks;
          } else if (ev.type === "token") {
            full += ev.text;
            body.innerHTML = marked.parse(full);
            body.appendChild(cursor);
            scrollChat();
          } else if (ev.type === "done") {
            cursor.remove();
            body.innerHTML = full.trim()
              ? marked.parse(full)
              : `<span style="color:var(--text-3)">The model returned an empty response.</span>`;
            if (ctxUsed > 0) {
              const badge = document.createElement("div");
              badge.className = "ctx-badge";
              badge.innerHTML = `<span>${ctxUsed}</span> chunks retrieved from ${state.activeGroups.size} group(s)`;
              aiRow.appendChild(badge);
            }
            scrollChat();
          } else if (ev.type === "error") {
            streamErrored = true;
            cursor.remove();
            body.innerHTML = `<span style="color:var(--error)">Error: ${esc(ev.text)}</span>`;
          }
        } catch {}
      }
    }
    if (!full.trim() && !streamErrored) {
      cursor.remove();
      body.innerHTML = `<span style="color:var(--text-3)">The model returned an empty response.</span>`;
    }
  } catch (e) {
    cursor.remove();
    body.innerHTML = `<span style="color:var(--error)">${esc(e.message || "Cannot reach backend - is it running?")}</span>`;
  }
}

// ── Semantic Search ───────────────────────────────────────────────────────────
async function doSearch(query) {
  appendUserMsg(query);

  const groupIds = state.activeGroups.size ? [...state.activeGroups] : state.groups.map(g => g.id);
  if (!groupIds.length) {
    appendAiMsg("No databases available. Index some PDFs first.");
    return;
  }

  // loading row
  const row = appendAiMsgStreaming();
  const body = row.querySelector(".msg-body");
  const cursor = row.querySelector(".cursor-blink");
  body.innerHTML = "Searching…";

  try {
    const r = await apiFetch("/api/search", {
      method: "POST",
      body: JSON.stringify({ query, group_ids: groupIds, top_k: 8 }),
    });
    const d = await r.json();
    cursor.remove();

    if (!d.results?.length) {
      body.innerHTML = `<span style="color:var(--text-3)">No matching documents found.</span>`;
      return;
    }

    body.innerHTML = `<div style="margin-bottom:10px;color:var(--text-2);font-size:13px">${d.results.length} results across ${d.matched_files.length} file(s)</div>`;

    const grid = document.createElement("div");
    grid.className = "search-grid";
    grid.style.paddingLeft = "0";
    d.results.forEach(res => {
      const grp = state.groups.find(g => g.id === res.group_id);
      const card = document.createElement("div");
      card.className = "search-card";
      card.innerHTML = `
        <div class="sc-file">
          <span class="color-dot" style="background:${esc(res.group_color)}"></span>
          ${esc(res.file)}
          <span class="sc-group">${esc(res.group_name)}</span>
        </div>
        <div class="sc-snippet">${esc(res.snippet)}…</div>
        <div class="sc-score">Similarity <b>${(res.score * 100).toFixed(1)}%</b></div>`;
      card.onclick = () => {
        // activate the group and switch to RAG
        if (res.group_id) state.activeGroups.add(res.group_id);
        renderGroupList();
        updateContextSummary();
        setMode("rag");
        quickPrompt(`Summarize what the document "${res.file}" says about: ${query}`);
        toast(`Context set to "${res.group_name}"`, "success");
      };
      grid.appendChild(card);
    });
    body.appendChild(grid);
    scrollChat();
  } catch (e) {
    cursor.remove();
    body.innerHTML = `<span style="color:var(--error)">Search failed: ${esc(e.message)}</span>`;
  }
}

// ── Message helpers ───────────────────────────────────────────────────────────
function appendUserMsg(text) {
  const msgs = document.getElementById("messages");
  const row  = document.createElement("div");
  row.className = "msg-row";
  const initial = (state.name || "U")[0].toUpperCase();
  row.innerHTML = `
    <div class="msg-header">
      <div class="msg-avatar user">${initial}</div>
      <span class="msg-name">${esc(state.name || state.username)}</span>
      <span class="msg-meta">${formatTime()}</span>
    </div>
    <div class="msg-body">${esc(text)}</div>`;
  msgs.appendChild(row);
  scrollChat();
  return row;
}

function appendAiMsg(html) {
  const msgs = document.getElementById("messages");
  const row  = document.createElement("div");
  row.className = "msg-row";
  row.innerHTML = `
    <div class="msg-header">
      <div class="msg-avatar ai">F</div>
      <span class="msg-name">Friday</span>
      <span class="msg-meta">${esc(state.model || "—")} · ${formatTime()}</span>
    </div>
    <div class="msg-body">${html}</div>`;
  msgs.appendChild(row);
  scrollChat();
  return row;
}

function appendAiMsgStreaming() {
  const msgs   = document.getElementById("messages");
  const row    = document.createElement("div");
  row.className = "msg-row";
  const cursor = document.createElement("span");
  cursor.className = "cursor-blink";
  row.innerHTML = `
    <div class="msg-header">
      <div class="msg-avatar ai">F</div>
      <span class="msg-name">Friday</span>
      <span class="msg-meta">${esc(state.model || "—")} · ${formatTime()}</span>
    </div>
    <div class="msg-body"></div>`;
  row.querySelector(".msg-body").appendChild(cursor);
  msgs.appendChild(row);
  scrollChat();
  return row;
}

function scrollChat() {
  const el = document.getElementById("chatArea");
  el.scrollTop = el.scrollHeight;
}

// ── Toast ─────────────────────────────────────────────────────────────────────
function toast(msg, type = "success") {
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 3200);
}

// ── Utils ─────────────────────────────────────────────────────────────────────
function esc(str) {
  return String(str ?? "")
    .replace(/&/g,"&amp;").replace(/</g,"&lt;")
    .replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

function formatTime() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function hexAlpha(hex, alpha) {
  const r = parseInt(hex.slice(1,3),16);
  const g = parseInt(hex.slice(3,5),16);
  const b = parseInt(hex.slice(5,7),16);
  return `rgba(${r},${g},${b},${alpha})`;
}

// Close menus on outside click
document.addEventListener("click", (e) => {
  const menu = document.getElementById("modelMenu");
  const sel  = document.getElementById("modelSelector");
  if (menu && !menu.contains(e.target) && !sel?.contains(e.target)) {
    menu.classList.remove("open");
    sel?.classList.remove("open");
  }
});

// Keyboard shortcut: Cmd/Ctrl+K focuses input
document.addEventListener("keydown", e => {
  if ((e.metaKey || e.ctrlKey) && e.key === "k") {
    e.preventDefault();
    document.getElementById("userInput")?.focus();
  }
});
