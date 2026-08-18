# SAI PRAVESH — Admission Portal (Flask backend)

End-to-end app: static frontend (`index.html`, `admin.html`) + Flask/Python backend + MySQL.
This replaces the old Node.js/Express backend (`index.js`/`server.js`) — routes, request/response
shapes, and session-based admin auth are unchanged, so the frontend needed zero edits.

## 1. Install
```bash
pip install -r requirements.txt
```

## 2. Set up MySQL
```bash
mysql -u root -p < schema.sql
```
This creates the `saipravesh` database and all 5 tables (`students`, `applications`,
`payments`, `health_records`, `uploads`).

## 3. Configure environment
```bash
cp .env.example .env
```
Edit `.env`:
- `DB_HOST` / `DB_USER` / `DB_PASS` / `DB_NAME` — your MySQL credentials
- `SESSION_SECRET` — any long random string
- `ADMIN_1` / `ADMIN_2` / `ADMIN_3` — admin accounts as `username:password:role:Display Name`
  (role must be `superadmin`, `director`, or `staff`)

**Set real passwords here, not the placeholders.** Don't commit `.env` to git — it's meant
to stay local (`.gitignore` below covers it).

## 4. Run
```bash
python app.py
```
Serves on `http://localhost:3000` — same port as the original.

## 5. Known gap — `script.js`
`index.html` references `<script src="/script.js"></script>` but that file wasn't included
in what was uploaded, so it's not part of this package. If your student-facing form logic
(steps 1–4: start application → course → payment → health record) lives in that file, add
it back into this folder — the backend routes it talks to (`/application/start`,
`/application/course`, `/payment/upload`, `/health`, `/application/status/:id`) are all
implemented in `app.py` and ready for it.

## File map
```
app.py              → all routes (student + admin)
db.py                → MySQL connection pool + query helper
admins_config.py     → loads admin accounts from .env
schema.sql           → database schema
requirements.txt     → Python dependencies
.env.example         → copy to .env and fill in
index.html           → student-facing site (unchanged)
admin.html           → admin dashboard (unchanged)
admin.js / admin.css → admin dashboard logic/styles (unchanged)
style.css            → student site styles (unchanged)
logo.png, atp.jpg, ad_block__3_.jpg → images (unchanged)
uploads/             → payment screenshots & admin docs land here at runtime
```

## Security note
The original code had a real DB password and admin passwords committed in plain text
(`db.js`, `admins.config.js`). Both are now pulled from `.env` instead, but since those
old credentials were shared in this conversation, rotate them before going live.
