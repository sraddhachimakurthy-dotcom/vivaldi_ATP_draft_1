/* ═══════════════════════════════════════════════
   SAI PRAVESH — Student Portal JS
   Wires index.html to the Flask backend routes:
   /application/start, /application/course,
   /payment/upload, /health, /application/status/<no>
═══════════════════════════════════════════════ */

let applicationId  = null;
let applicationNo  = "";

/* Programme lists per level — edit freely to match the real prospectus */
const COURSES = {
  Undergraduate: [
    "B.A. English Language and Literature",
    "B.A. Economics",
    "B.Sc. Mathematics",
    "B.Sc. Physics",
    "B.Sc. Chemistry",
    "B.Sc. Computer Science",
    "B.Sc. Biosciences",
    "B.Com."
  ],
  Postgraduate: [
    "M.A. English Language and Literature",
    "M.A. Economics",
    "M.Sc. Mathematics",
    "M.Sc. Physics",
    "M.Sc. Chemistry",
    "M.Sc. Biosciences",
    "M.Sc. Food and Nutritional Sciences",
    "MBA",
    "MCA"
  ]
};

/* ── PAGE NAVIGATION ── */
const STEP_PAGES = {
  "page1": 1,
  "page2": 2,
  "payment-page": 3,
  "health-page": 4,
  "success-page": 5
};

function showPage(id) {
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
  const target = document.getElementById(id);
  if (target) target.classList.add("active");

  // Nav button highlight (Home/Forms/Status/Help)
  document.querySelectorAll(".header-nav .nav-btn").forEach(b => b.classList.remove("active"));

  // Progress bar only for the application steps
  const bar = document.getElementById("progress-bar");
  if (STEP_PAGES[id]) {
    bar.classList.remove("hidden");
    updateSteps(STEP_PAGES[id]);
  } else {
    bar.classList.add("hidden");
  }

  if (id === "forms-page") loadForms();

  window.scrollTo(0, 0);
}

function updateSteps(current) {
  for (let i = 1; i <= 5; i++) {
    const el = document.getElementById(`step-${i}`);
    if (!el) continue;
    el.classList.remove("active", "done");
    if (i < current) el.classList.add("done");
    else if (i === current) el.classList.add("active");
  }
}

function startApplication() {
  showPage("page1");
}

/* ── STEP 1 — DETAILS ── */
function saveApplication() {
  const errorEl = document.getElementById("error-page1");
  errorEl.style.display = "none";

  const admissionNumber = document.getElementById("admissionNumber").value.trim();
  const candidateName   = document.getElementById("candidateName").value.trim();
  const dob              = document.getElementById("dob").value;
  const email             = document.getElementById("email").value.trim();
  const mobile            = document.getElementById("mobile").value.trim();
  const category          = document.getElementById("category").value;
  const decl               = document.getElementById("decl1").checked;

  if (!admissionNumber || !candidateName) {
    errorEl.textContent = "Application number and full name are required.";
    errorEl.style.display = "block";
    return;
  }
  if (!decl) {
    errorEl.textContent = "Please confirm the declaration to continue.";
    errorEl.style.display = "block";
    return;
  }

  fetch("/application/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      application_number: admissionNumber,
      candidate_name: candidateName,
      email, mobile, dob, category
    })
  })
  .then(r => r.json())
  .then(d => {
    if (d.error) {
      errorEl.textContent = d.error;
      errorEl.style.display = "block";
      return;
    }
    applicationId = d.application_id;
    applicationNo = admissionNumber;
    showPage("page2");
  })
  .catch(() => {
    errorEl.textContent = "Network error. Please try again.";
    errorEl.style.display = "block";
  });
}

/* ── STEP 2 — COURSE ── */
const courseLevelSelect = document.getElementById("courseLevel");
if (courseLevelSelect) {
  courseLevelSelect.addEventListener("change", () => {
    const level = courseLevelSelect.value;
    const nameSelect = document.getElementById("courseName");
    nameSelect.innerHTML = '<option value="">-- Select Programme --</option>';
    (COURSES[level] || []).forEach(name => {
      const opt = document.createElement("option");
      opt.value = name;
      opt.textContent = name;
      nameSelect.appendChild(opt);
    });
  });
}

function saveCourse() {
  const errorEl = document.getElementById("error-page2");
  errorEl.style.display = "none";

  if (!applicationId) {
    errorEl.textContent = "Please complete Step 1 first.";
    errorEl.style.display = "block";
    showPage("page1");
    return;
  }

  const courseLevel = document.getElementById("courseLevel").value;
  const courseName  = document.getElementById("courseName").value;
  const decl         = document.getElementById("decl2").checked;

  if (!courseLevel || !courseName) {
    errorEl.textContent = "Please select a programme level and name.";
    errorEl.style.display = "block";
    return;
  }
  if (!decl) {
    errorEl.textContent = "Please confirm the declaration to continue.";
    errorEl.style.display = "block";
    return;
  }

  fetch("/application/course", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ application_id: applicationId, course_level: courseLevel, course_name: courseName })
  })
  .then(r => r.json())
  .then(d => {
    if (d.error) {
      errorEl.textContent = d.error;
      errorEl.style.display = "block";
      return;
    }
    showPage("payment-page");
  })
  .catch(() => {
    errorEl.textContent = "Network error. Please try again.";
    errorEl.style.display = "block";
  });
}

/* ── STEP 3 — PAYMENT ── */
function previewFile(input) {
  const preview = document.getElementById("file-preview");
  const zone = document.getElementById("uploadZone");
  if (input.files && input.files[0]) {
    preview.textContent = `Selected: ${input.files[0].name}`;
    zone.classList.add("has-file");
  } else {
    preview.textContent = "";
    zone.classList.remove("has-file");
  }
}

function uploadPayment() {
  const errorEl = document.getElementById("error-payment");
  errorEl.style.display = "none";

  if (!applicationId) {
    errorEl.textContent = "Please complete Step 1 first.";
    errorEl.style.display = "block";
    showPage("page1");
    return;
  }

  const fileInput = document.getElementById("paymentFile");
  const file = fileInput.files[0];
  if (!file) {
    errorEl.textContent = "Please select a payment proof file.";
    errorEl.style.display = "block";
    return;
  }

  const fd = new FormData();
  fd.append("application_id", applicationId);
  fd.append("payment_file", file);

  fetch("/payment/upload", { method: "POST", body: fd })
  .then(r => r.json())
  .then(d => {
    if (d.error) {
      errorEl.textContent = d.error;
      errorEl.style.display = "block";
      return;
    }
    showPage("health-page");
  })
  .catch(() => {
    errorEl.textContent = "Network error. Please try again.";
    errorEl.style.display = "block";
  });
}

/* ── STEP 4 — HEALTH RECORD ── */
function saveHealth() {
  const errorEl = document.getElementById("error-health");
  errorEl.style.display = "none";

  if (!applicationId) {
    errorEl.textContent = "Please complete Step 1 first.";
    errorEl.style.display = "block";
    showPage("page1");
    return;
  }

  const age         = document.getElementById("age").value;
  const bloodGroup  = document.getElementById("bloodGroup").value;
  const decl         = document.getElementById("decl4").checked;

  if (!age || !bloodGroup) {
    errorEl.textContent = "Age and blood group are required.";
    errorEl.style.display = "block";
    return;
  }
  if (!decl) {
    errorEl.textContent = "Please confirm the declaration to continue.";
    errorEl.style.display = "block";
    return;
  }

  const payload = {
    application_id: applicationId,
    age,
    height: document.getElementById("height").value,
    weight: document.getElementById("weight").value,
    bloodGroup,
    identificationMark1: document.getElementById("idMark1").value.trim(),
    identificationMark2: document.getElementById("idMark2").value.trim(),
    asthma: document.getElementById("asthma").value,
    diabetes: document.getElementById("diabetes").value,
    epilepsy: document.getElementById("epilepsy").value,
    cardiac: document.getElementById("cardiac").value,
    tuberculosis: document.getElementById("tb").value,
    hepb: document.getElementById("hepb").value,
    covidDose: document.getElementById("covidDose").value,
    familyDiabetes: document.getElementById("famDiabetes").value,
    familyEpilepsy: document.getElementById("famEpilepsy").value,
    familyTB: document.getElementById("famTB").value
  };

  fetch("/health", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  })
  .then(r => r.json())
  .then(d => {
    if (d.error) {
      errorEl.textContent = d.error;
      errorEl.style.display = "block";
      return;
    }
    document.getElementById("success-app-id").textContent = applicationNo || applicationId;
    showPage("success-page");
  })
  .catch(() => {
    errorEl.textContent = "Network error. Please try again.";
    errorEl.style.display = "block";
  });
}

/* ── STATUS CHECK ── */
function checkStatus() {
  const input = document.getElementById("statusInput").value.trim();
  const resultBox = document.getElementById("statusResult");
  if (!input) return;

  fetch(`/application/status/${encodeURIComponent(input)}`)
  .then(r => r.json())
  .then(d => {
    resultBox.classList.remove("hidden");
    const statusText  = document.getElementById("statusText");
    const statusName  = document.getElementById("statusName");
    const statusCourse = document.getElementById("statusCourse");

    if (d.error || d.status === "Not Found") {
      statusText.textContent = "Not Found";
      statusText.className = "status-value status-not-found";
      statusName.textContent = "";
      statusCourse.textContent = "";
      return;
    }

    statusText.textContent = d.status;
    statusText.className = "status-value " + statusClass(d.status);
    statusName.textContent = d.full_name || "";
    statusCourse.textContent = d.course_name ? `Programme: ${d.course_name}` : "";
  })
  .catch(() => {
    resultBox.classList.remove("hidden");
    document.getElementById("statusText").textContent = "Error checking status";
  });
}

function statusClass(status) {
  const map = {
    "Started": "status-started",
    "Course Selected": "status-course-selected",
    "Payment Uploaded": "status-payment-uploaded",
    "Completed": "status-completed",
    "Approved": "status-approved",
    "Rejected": "status-rejected",
    "Locked": "status-locked"
  };
  return map[status] || "";
}

/* ── FORMS PAGE ── */
function loadForms() {
  const list = document.getElementById("forms-list");
  fetch("/forms")
  .then(r => r.json())
  .then(rows => {
    if (!rows.length) {
      list.innerHTML = `<p class="loading-text">No documents uploaded yet.</p>`;
      return;
    }
    list.innerHTML = rows.map(f => `
      <a href="/uploads/${f.filename}" target="_blank" class="form-item">
        <span class="form-icon">📄</span>
        <span>${f.doc_name}</span>
      </a>
    `).join("");
  })
  .catch(() => {
    list.innerHTML = `<p class="loading-text">Could not load documents.</p>`;
  });
}

/* ── LANDING SLIDESHOW (skips any image that fails to load) ── */
(function initSlideshow() {
  const slides = Array.from(document.querySelectorAll(".slide"));
  if (slides.length < 2) return;

  let workingSlides = [];
  let checked = 0;

  slides.forEach(slide => {
    const bg = slide.style.backgroundImage.slice(5, -2); // url("...") -> ...
    const img = new Image();
    img.onload = () => { workingSlides.push(slide); afterCheck(); };
    img.onerror = () => { slide.remove(); afterCheck(); };
    img.src = bg;
  });

  function afterCheck() {
    checked++;
    if (checked === slides.length && workingSlides.length > 1) {
      startRotation(workingSlides);
    }
  }

  function startRotation(list) {
    let i = 0;
    setInterval(() => {
      list[i].classList.remove("active");
      i = (i + 1) % list.length;
      list[i].classList.add("active");
    }, 5000);
  }
})();