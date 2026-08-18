"""
SAI PRAVESH — Flask backend
Port of the original Node.js/Express (index.js) backend.

Run:
    pip install -r requirements.txt
    cp .env.example .env   # then edit .env with real values
    python app.py
"""

import os
import time
import random
import string
from functools import wraps

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, session, send_from_directory
from werkzeug.utils import secure_filename

import db
from admins_config import ADMINS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")
app.secret_key = os.getenv("SESSION_SECRET", "change_this_secret")
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE
app.permanent_session_lifetime = 60 * 60 * 2  # 2 hours, mirrors cookie.maxAge


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def unique_filename(original_name):
    ext = os.path.splitext(original_name)[1].lower()
    rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{int(time.time() * 1000)}_{rand}{ext}"


def save_upload(file_storage):
    """Validate extension/size and save file. Returns filename or raises ValueError."""
    if file_storage is None or file_storage.filename == "":
        raise ValueError("No file uploaded or invalid file type")

    ext = os.path.splitext(file_storage.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Only JPG, PNG, PDF files are allowed")

    filename = unique_filename(secure_filename(file_storage.filename))
    filepath = os.path.join(UPLOAD_DIR, filename)
    file_storage.save(filepath)
    return filename


def check_admin(f):
    """Equivalent to checkAdmin middleware."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return jsonify({"error": "Unauthorized"}), 403
        return f(*args, **kwargs)
    return wrapper


def require_role(*roles):
    """Equivalent to requireRole(...roles) middleware factory."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not session.get("admin"):
                return jsonify({"error": "Unauthorized"}), 403
            if session.get("role") not in roles:
                return jsonify({"error": "Insufficient permissions"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator


# ══════════════════════════════════════
# STUDENT ROUTES
# ══════════════════════════════════════

@app.post("/application/start")
def application_start():
    data = request.get_json(silent=True) or {}
    application_number = data.get("application_number")
    candidate_name = data.get("candidate_name")
    email = data.get("email")
    mobile = data.get("mobile")
    dob = data.get("dob")
    category = data.get("category")

    if not application_number or not candidate_name:
        return jsonify({"error": "Application number and name are required"})

    try:
        existing = db.query(
            "SELECT id FROM students WHERE admission_number = %s",
            (application_number,),
        )

        if existing:
            student_id = existing[0]["id"]
            app_row = db.query(
                "SELECT id FROM applications WHERE student_id = %s",
                (student_id,),
            )
            if not app_row:
                return jsonify({"error": "Application record missing for this student."})
            return jsonify({"application_id": app_row[0]["id"], "resumed": True})

        student_id, _ = db.query(
            """INSERT INTO students (admission_number, full_name, email, mobile, dob, category)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (application_number, candidate_name, email or None, mobile or None, dob or None, category or None),
            fetch=False,
        )

        app_id, _ = db.query(
            "INSERT INTO applications (student_id, status) VALUES (%s, 'Started')",
            (student_id,),
            fetch=False,
        )

        return jsonify({"application_id": app_id})

    except Exception as e:
        return jsonify({"error": str(e)})


@app.post("/application/course")
def application_course():
    data = request.get_json(silent=True) or {}
    application_id = data.get("application_id")
    course_level = data.get("course_level")
    course_name = data.get("course_name")

    if not application_id or not course_level or not course_name:
        return jsonify({"error": "All fields required"})

    try:
        db.query(
            "UPDATE applications SET course_level=%s, course_name=%s, status='Course Selected' WHERE id=%s",
            (course_level, course_name, application_id),
            fetch=False,
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.post("/payment/upload")
def payment_upload():
    application_id = request.form.get("application_id")

    try:
        filename = save_upload(request.files.get("payment_file"))
    except ValueError as e:
        return jsonify({"error": str(e)})

    try:
        db.query(
            """INSERT INTO payments (application_id, screenshot_path) VALUES (%s, %s)
               ON DUPLICATE KEY UPDATE screenshot_path=%s""",
            (application_id, filename, filename),
            fetch=False,
        )
        db.query(
            "UPDATE applications SET status='Payment Uploaded' WHERE id=%s",
            (application_id,),
            fetch=False,
        )
        return jsonify({"success": True, "filename": filename})
    except Exception as e:
        return jsonify({"error": str(e)})


def _num_or_none(value):
    """Coerce '' / None to NULL for numeric DB columns; leave real values alone."""
    if value is None or value == "":
        return None
    return value


@app.post("/health")
def health_record():
    d = request.get_json(silent=True) or {}
    application_id = d.get("application_id")
    if not application_id:
        return jsonify({"error": "Application ID required"})

    try:
        db.query(
            """INSERT INTO health_records
               (application_id, age, height_cm, weight_kg, blood_group,
                identification_mark1, identification_mark2,
                asthma, diabetes, epilepsy, cardiac, tuberculosis,
                covid_dose, hep_b,
                family_diabetes, family_epilepsy, family_tb)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
               ON DUPLICATE KEY UPDATE
                age=VALUES(age), height_cm=VALUES(height_cm), weight_kg=VALUES(weight_kg),
                blood_group=VALUES(blood_group)""",
            (
                application_id, _num_or_none(d.get("age")), _num_or_none(d.get("height")),
                _num_or_none(d.get("weight")), d.get("bloodGroup"),
                d.get("identificationMark1") or None, d.get("identificationMark2") or None,
                d.get("asthma") or "No", d.get("diabetes") or "No", d.get("epilepsy") or "No",
                d.get("cardiac") or "No", d.get("tuberculosis") or "No",
                d.get("covidDose") or None, d.get("hepb") or "No",
                d.get("familyDiabetes") or "No", d.get("familyEpilepsy") or "No", d.get("familyTB") or "No",
            ),
            fetch=False,
        )
        db.query(
            "UPDATE applications SET status='Completed' WHERE id=%s",
            (application_id,),
            fetch=False,
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.get("/application/status/<app_no>")
def application_status(app_no):
    try:
        rows = db.query(
            """SELECT a.status, a.id, s.full_name, a.course_name
               FROM applications a
               JOIN students s ON a.student_id = s.id
               WHERE s.admission_number = %s""",
            (app_no,),
        )
        if not rows:
            return jsonify({"status": "Not Found"})
        return jsonify(rows[0])
    except Exception as e:
        return jsonify({"error": str(e)})


# ══════════════════════════════════════
# ADMIN ROUTES
# ══════════════════════════════════════

@app.post("/admin/login")
def admin_login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    match = next(
        (a for a in ADMINS if a["username"] == username and a["password"] == password),
        None,
    )

    if match:
        session.permanent = True
        session["admin"] = True
        session["role"] = match["role"]
        session["name"] = match["name"]
        return jsonify({"success": True, "role": match["role"], "name": match["name"]})

    return jsonify({"success": False, "error": "Invalid credentials"})


@app.post("/admin/logout")
def admin_logout():
    session.clear()
    return jsonify({"success": True})


@app.get("/admin/me")
def admin_me():
    if not session.get("admin"):
        return jsonify({"loggedIn": False})
    return jsonify({"loggedIn": True, "role": session.get("role"), "name": session.get("name")})


@app.get("/admin/applications")
@check_admin
def admin_applications():
    try:
        rows = db.query(
            """SELECT a.id, s.admission_number, s.full_name, s.email, s.mobile,
                      a.course_level, a.course_name, a.status, a.created_at
               FROM applications a
               JOIN students s ON a.student_id = s.id
               ORDER BY a.created_at DESC"""
        )
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)})


@app.get("/admin/application/<int:app_id>")
@check_admin
def admin_application_detail(app_id):
    try:
        rows = db.query(
            """SELECT s.admission_number, s.full_name, s.email, s.mobile, s.dob, s.category,
                      a.course_level, a.course_name, a.status, a.created_at,
                      p.screenshot_path,
                      h.age, h.height_cm, h.weight_kg, h.blood_group,
                      h.identification_mark1, h.identification_mark2,
                      h.asthma, h.diabetes, h.epilepsy, h.cardiac, h.tuberculosis,
                      h.covid_dose, h.hep_b, h.family_diabetes, h.family_epilepsy, h.family_tb
               FROM applications a
               JOIN students s ON a.student_id = s.id
               LEFT JOIN payments p ON p.application_id = a.id
               LEFT JOIN health_records h ON h.application_id = a.id
               WHERE a.id = %s""",
            (app_id,),
        )
        if not rows:
            return jsonify({"error": "Not found"})
        return jsonify(rows[0])
    except Exception as e:
        return jsonify({"error": str(e)})


@app.get("/admin/stats")
@check_admin
def admin_stats():
    try:
        rows = db.query(
            """SELECT
                COUNT(*) as total,
                SUM(status='Started') as started,
                SUM(status='Course Selected') as course_selected,
                SUM(status='Payment Uploaded') as payment_uploaded,
                SUM(status='Completed') as completed,
                SUM(status='Approved') as approved,
                SUM(status='Rejected') as rejected,
                SUM(status='Locked') as locked
               FROM applications"""
        )
        return jsonify(rows[0])
    except Exception as e:
        return jsonify({"error": str(e)})


@app.post("/admin/status")
@require_role("superadmin", "director", "staff")
def admin_update_status():
    data = request.get_json(silent=True) or {}
    app_id = data.get("id")
    status = data.get("status")
    role = session.get("role")

    staff_allowed = {"Completed"}
    senior_allowed = {"Approved", "Rejected", "Pending Verification", "Completed"}
    allowed = staff_allowed if role == "staff" else senior_allowed

    if status not in allowed:
        return jsonify({"error": "You do not have permission to set this status"})

    try:
        db.query(
            "UPDATE applications SET status=%s WHERE id=%s AND status != 'Locked'",
            (status, app_id),
            fetch=False,
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.post("/admin/lock")
@require_role("superadmin")
def admin_lock():
    data = request.get_json(silent=True) or {}
    app_id = data.get("id")
    try:
        db.query(
            "UPDATE applications SET status='Locked' WHERE id=%s",
            (app_id,),
            fetch=False,
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.post("/admin/upload")
@require_role("superadmin")
def admin_upload():
    doc_name = request.form.get("doc_name")

    try:
        filename = save_upload(request.files.get("file"))
    except ValueError as e:
        return jsonify({"error": str(e)})

    try:
        db.query(
            """INSERT INTO uploads (doc_name, filename) VALUES (%s, %s)
               ON DUPLICATE KEY UPDATE filename=%s, uploaded_at=NOW()""",
            (doc_name, filename, filename),
            fetch=False,
        )
        return jsonify({"success": True, "filename": filename})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.get("/forms")
def forms_list():
    try:
        rows = db.query("SELECT * FROM uploads ORDER BY uploaded_at DESC")
        return jsonify(rows)
    except Exception:
        return jsonify([])


# ══════════════════════════════════════
# STATIC FILES (uploads, root-level assets)
# ══════════════════════════════════════

@app.get("/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory(UPLOAD_DIR, filename)


@app.get("/")
def serve_index():
    return send_from_directory(BASE_DIR, "index.html")


@app.get("/admin")
def serve_admin():
    return send_from_directory(BASE_DIR, "admin.html")


# ──────────────────────────────────────────────
# Error handler (mirrors the Express error middleware)
# ──────────────────────────────────────────────

@app.errorhandler(Exception)
def handle_error(e):
    code = getattr(e, "code", 500)
    if not isinstance(code, int):
        code = 500
    app.logger.error(str(e))
    return jsonify({"error": str(e)}), code


if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    app.run(host="0.0.0.0", port=port, debug=True)