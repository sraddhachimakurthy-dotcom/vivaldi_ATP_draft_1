/* ═══════════════════════════════════════════════
   SAI PRAVESH — Admin Portal JS (Browser Only)
   Roles: superadmin | director | staff
═══════════════════════════════════════════════ */

let allApps     = [];
let currentRole = "";
let currentName = "";

/* ── LOGIN ── */
function adminLogin() {
  const u = document.getElementById("adminUser").value.trim();
  const p = document.getElementById("adminPass").value;

  if (!u || !p) {
    document.getElementById("loginError").textContent = "Please enter credentials";
    return;
  }

  fetch("/admin/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: u, password: p })
  })
  .then(r => r.json())
  .then(d => {
    if (d.success) {
      currentRole = d.role;
      currentName = d.name;

      // Switch screens
      document.getElementById("loginBox").style.display    = "none";
      document.getElementById("dashboard").style.display   = "block";

      // Show logged-in user info
      document.getElementById("loggedInAs").textContent = `${currentName} (${currentRole})`;

      // Hide upload section for non-superadmin
      if (currentRole !== "superadmin") {
        const uploadSec = document.getElementById("uploadSection");
        if (uploadSec) uploadSec.style.display = "none";
      }

      refreshAll();
    } else {
      document.getElementById("loginError").textContent = d.error || "Invalid credentials";
    }
  })
  .catch(() => {
    document.getElementById("loginError").textContent = "Network error. Try again.";
  });
}

// Allow Enter key on login
document.addEventListener("keydown", e => {
  const box = document.getElementById("loginBox");
  if (e.key === "Enter" && box && box.style.display !== "none") adminLogin();
});

/* ── LOGOUT ── */
function adminLogout() {
  fetch("/admin/logout", { method: "POST" }).then(() => location.reload());
}

/* ── REFRESH ALL ── */
function refreshAll() {
  loadStats();
  loadApps();
}

/* ── STATS ── */
function loadStats() {
  fetch("/admin/stats")
  .then(r => r.json())
  .then(d => {
    document.getElementById("st-total").textContent     = d.total     || 0;
    document.getElementById("st-started").textContent   = d.started   || 0;
    document.getElementById("st-completed").textContent = d.completed || 0;
    document.getElementById("st-approved").textContent  = d.approved  || 0;
    document.getElementById("st-rejected").textContent  = d.rejected  || 0;
    document.getElementById("st-locked").textContent    = d.locked    || 0;
  })
  .catch(() => console.error("Failed to load stats"));
}

/* ── LOAD APPLICATIONS ── */
function loadApps() {
  fetch("/admin/applications")
  .then(r => r.json())
  .then(data => {
    allApps = data;
    renderTable(data);
  })
  .catch(() => console.error("Failed to load applications"));
}

/* ── RENDER TABLE ── */
function renderTable(data) {
  const tbody = document.getElementById("appTable");
  if (!tbody) return;

  if (!data.length) {
    tbody.innerHTML = `<tr class="empty-row"><td colspan="6">No applications found</td></tr>`;
    return;
  }

  // Role permissions
  const canApproveReject = ["superadmin", "director"].includes(currentRole);
  const canLock          = currentRole === "superadmin";
  const canVerify        = currentRole === "staff";

  tbody.innerHTML = data.map((a, i) => `
    <tr>
      <td>${i + 1}</td>
      <td>${a.admission_number || "—"}</td>
      <td>${a.full_name}</td>
      <td>${a.course_name || "<span style='color:var(--muted)'>Not selected</span>"}</td>
      <td><span class="badge ${badgeClass(a.status)}">${a.status}</span></td>
      <td>
        <div class="action-btns">
          <!-- All roles can view -->
          <button class="btn-act btn-view" onclick="viewApp(${a.id})">View</button>

          <!-- Staff: can mark payment verified -->
          ${canVerify && a.status === "Payment Uploaded" ? `
            <button class="btn-act btn-approve" onclick="updateStatus(${a.id},'Completed')" title="Mark as Verified">✔ Verify</button>
          ` : ""}

          <!-- Director + Superadmin: approve / reject -->
          ${canApproveReject && a.status !== "Locked" ? `
            <button class="btn-act btn-approve" onclick="updateStatus(${a.id},'Approved')">Approve</button>
            <button class="btn-act btn-reject"  onclick="updateStatus(${a.id},'Rejected')">Reject</button>
          ` : ""}

          <!-- Superadmin only: lock -->
          ${canLock && a.status !== "Locked" ? `
            <button class="btn-act btn-lock" onclick="lockApp(${a.id})">Lock</button>
          ` : ""}

          ${a.status === "Locked" ? `<span style="color:var(--muted);font-size:0.8rem;">🔒 Locked</span>` : ""}
        </div>
      </td>
    </tr>
  `).join("");
}

/* ── BADGE CLASS ── */
function badgeClass(status) {
  const map = {
    "Started":          "badge-started",
    "Course Selected":  "badge-course",
    "Payment Uploaded": "badge-payment",
    "Completed":        "badge-completed",
    "Approved":         "badge-approved",
    "Rejected":         "badge-rejected",
    "Locked":           "badge-locked"
  };
  return map[status] || "badge-started";
}

/* ── FILTER TABLE ── */
function filterTable() {
  const q = document.getElementById("searchInput").value.toLowerCase();
  const s = document.getElementById("statusFilter").value;
  const filtered = allApps.filter(a =>
    (!q || a.full_name.toLowerCase().includes(q) || (a.admission_number || "").toLowerCase().includes(q)) &&
    (!s || a.status === s)
  );
  renderTable(filtered);
}

/* ── VIEW POPUP ── */
function viewApp(id) {
  fetch(`/admin/application/${id}`)
  .then(r => r.json())
  .then(d => {
    if (d.error) return alert(d.error);

    document.getElementById("popupContent").innerHTML = `
      <h3>${d.full_name}</h3>

      <div class="popup-grid">
        <div class="popup-field"><label>Application No</label><p>${d.admission_number || "—"}</p></div>
        <div class="popup-field"><label>Email</label><p>${d.email || "—"}</p></div>
        <div class="popup-field"><label>Mobile</label><p>${d.mobile || "—"}</p></div>
        <div class="popup-field"><label>Date of Birth</label><p>${d.dob ? new Date(d.dob).toLocaleDateString("en-IN") : "—"}</p></div>
        <div class="popup-field"><label>Category</label><p>${d.category || "—"}</p></div>
        <div class="popup-field"><label>Status</label><p><span class="badge ${badgeClass(d.status)}">${d.status}</span></p></div>
        <div class="popup-field"><label>Course Level</label><p>${d.course_level || "—"}</p></div>
        <div class="popup-field"><label>Programme</label><p>${d.course_name || "—"}</p></div>
      </div>

      ${d.screenshot_path ? `
        <p style="font-size:0.78rem;color:var(--muted);margin-bottom:6px;text-transform:uppercase;letter-spacing:.05em;">Payment Proof</p>
        <img src="/uploads/${d.screenshot_path}" class="popup-img" onerror="this.style.display='none'">
      ` : `<p style="color:var(--muted);margin-bottom:12px;">No payment uploaded yet</p>`}

      ${d.age ? `
        <p style="font-size:0.78rem;color:var(--muted);margin:16px 0 8px;text-transform:uppercase;letter-spacing:.05em;">Health Record</p>
        <div class="popup-grid">
          <div class="popup-field"><label>Age</label><p>${d.age}</p></div>
          <div class="popup-field"><label>Blood Group</label><p>${d.blood_group || "—"}</p></div>
          <div class="popup-field"><label>Height</label><p>${d.height_cm ? d.height_cm + " cm" : "—"}</p></div>
          <div class="popup-field"><label>Weight</label><p>${d.weight_kg ? d.weight_kg + " kg" : "—"}</p></div>
          <div class="popup-field"><label>Asthma</label><p>${d.asthma || "—"}</p></div>
          <div class="popup-field"><label>Diabetes</label><p>${d.diabetes || "—"}</p></div>
          <div class="popup-field"><label>Epilepsy</label><p>${d.epilepsy || "—"}</p></div>
          <div class="popup-field"><label>Cardiac</label><p>${d.cardiac || "—"}</p></div>
          <div class="popup-field"><label>COVID Doses</label><p>${d.covid_dose || "—"}</p></div>
          <div class="popup-field"><label>Hepatitis B</label><p>${d.hep_b || "—"}</p></div>
          <div class="popup-field"><label>Family — Diabetes</label><p>${d.family_diabetes || "—"}</p></div>
          <div class="popup-field"><label>Family — Epilepsy</label><p>${d.family_epilepsy || "—"}</p></div>
          <div class="popup-field"><label>Family — TB</label><p>${d.family_tb || "—"}</p></div>
        </div>
      ` : ""}

      <button class="popup-close" onclick="closePopup()">Close</button>
    `;

    document.getElementById("popupOverlay").classList.add("active");
  })
  .catch(() => alert("Failed to load application details"));
}

function closePopup(e) {
  if (!e || e.target === document.getElementById("popupOverlay")) {
    document.getElementById("popupOverlay").classList.remove("active");
  }
}

/* ── STATUS UPDATE (director + superadmin) ── */
function updateStatus(id, status) {
  if (!confirm(`Set application #${id} to "${status}"?`)) return;
  fetch("/admin/status", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id, status })
  })
  .then(r => r.json())
  .then(d => {
    if (d.error) return alert(d.error);
    refreshAll();
  });
}

/* ── LOCK (superadmin only) ── */
function lockApp(id) {
  if (!confirm(`Lock application #${id}? This cannot be undone.`)) return;
  fetch("/admin/lock", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id })
  })
  .then(r => r.json())
  .then(d => {
    if (d.error) return alert(d.error);
    refreshAll();
  });
}

/* ── UPLOAD DOC (superadmin only) ── */
function uploadDoc() {
  const name = document.getElementById("docName").value.trim();
  const file = document.getElementById("docFile").files[0];
  const msg  = document.getElementById("uploadMsg");

  if (!name || !file) {
    msg.style.color = "var(--red)";
    msg.textContent = "Please enter a document name and select a file";
    return;
  }

  const fd = new FormData();
  fd.append("doc_name", name);
  fd.append("file", file);

  fetch("/admin/upload", { method: "POST", body: fd })
  .then(r => r.json())
  .then(d => {
    if (d.success) {
      msg.style.color = "var(--green)";
      msg.textContent = "✓ Document uploaded successfully";
      document.getElementById("docName").value = "";
      document.getElementById("docFile").value = "";
    } else {
      msg.style.color = "var(--red)";
      msg.textContent = d.error || "Upload failed";
    }
  });
}