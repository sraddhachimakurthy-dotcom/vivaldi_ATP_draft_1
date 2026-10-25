# 🌸 SAI PRAVESH — Admission Portal (Flask Backend & Frontend)

Welcome to **SAI PRAVESH**, the online admission and student onboarding portal for **Sri Sathya Sai Institute of Higher Learning (Anantapur Campus)**.

This repository contains a complete, production-ready web application built with a **Flask (Python) backend**, a **MySQL database**, and a clean **HTML/CSS/JS frontend**.

---

## 👶 Beginner's Guide: Setting Up & Running Locally (Step-by-Step)

If you are new to programming or database setup, follow these simple steps carefully!

---

### Step 1: Install MySQL on Your Computer

MySQL is the database system where all student details, applications, health records, and payments will be safely stored.

#### 🪟 On Windows:
1. Download the **MySQL Installer for Windows** from the official site: [https://dev.mysql.com/downloads/installer/](https://dev.mysql.com/downloads/installer/)
2. Run the downloaded `.msi` setup file.
3. Choose **Developer Default** or **Full Installation**.
4. During setup, set a **Root Password** (for example: `MyRootPass123!`). **Remember this password!**
5. Finish installation and open **MySQL Workbench** or **MySQL Command Line Client**.

#### 🍎 On macOS:
1. The easiest way is using **Homebrew**:
   ```bash
   brew install mysql
   brew services start mysql
   ```
2. Set root password:
   ```bash
   mysql_secure_installation
   ```

#### 🐧 On Linux (Ubuntu/Debian):
1. Run:
   ```bash
   sudo apt update
   sudo apt install mysql-server -y
   sudo systemctl start mysql
   ```
2. Secure installation:
   ```bash
   sudo mysql_secure_installation
   ```

---

### Step 2: Initialize the Database (`saipravesh`)

1. Open your terminal or command prompt in the project root folder.
2. Run the SQL schema script to create the database and required tables:
   ```bash
   mysql -u root -p < schema.sql
   ```
   *(Enter your MySQL root password when prompted)*

3. Verify tables were created by running:
   ```bash
   mysql -u root -p -e "USE saipravesh; SHOW TABLES;"
   ```
   You should see 5 tables:
   - `applications`
   - `health_records`
   - `payments`
   - `students`
   - `uploads`

---

### Step 3: Set Up Python Dependencies

1. Open terminal in the project folder.
2. (Optional but recommended) Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate        # On macOS/Linux
   venv\Scripts\activate           # On Windows
   ```
3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

---

### Step 4: Configure Your Environment Variables (`.env`)

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` in a text editor (like VS Code, Notepad, or Nano) and update the values:

   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASS=your_real_mysql_password
   DB_NAME=saipravesh

   SESSION_SECRET=a_very_long_and_secret_random_string_here

   # Admin Logins -> format: username:password:role:Display Name
   ADMIN_1=admin:AdminPass123!:superadmin:Super Administrator
   ADMIN_2=director:DirectorPass123!:director:Campus Director
   ADMIN_3=admissions:StaffPass123!:staff:Admissions Staff
   ```

---

### Step 5: Run the Application Locally!

1. Start the Flask app:
   ```bash
   python app.py
   ```
2. Open your web browser and navigate to:
   - **Student Portal:** `http://localhost:3000`
   - **Admin Portal:** `http://localhost:3000/admin.html`

3. **Try out the workflow:**
   - **Step 1:** Enter Student Details (Application Number, Name, Email, DOB).
   - **Step 2:** Choose Academic Programme Level and Name.
   - **Step 3:** Upload payment screenshot/receipt (JPG/PNG/PDF up to 5MB).
   - **Step 4:** Fill Health Record details and submit.
   - **Step 5:** Copy your Application Number, go to **Status**, and check application status.
   - **Admin:** Open `http://localhost:3000/admin.html`, log in using `admin` / `AdminPass123!`. Review, verify, approve, or reject applications!

---

### Step 6: Run Unit Tests

To verify that every part of the application backend works correctly:
```bash
python3 -m unittest test_app.py
```

---

## 🚀 Deployment Checklist for Production

To make this app completely deployment-ready on a cloud server (AWS, DigitalOcean, Hetzner, GCP, Azure, PythonAnywhere, Render, or VPS):

### 1. WSGI Server (Gunicorn or Waitress)
- Do **NOT** use `python app.py` (Flask built-in server) in production.
- Install Gunicorn (for Linux):
  ```bash
  pip install gunicorn
  gunicorn -w 4 -b 127.0.0.1:3000 app:app
  ```
- Or Waitress (for Windows server):
  ```bash
  pip install waitress
  waitress-serve --port=3000 app:app
  ```

### 2. Reverse Proxy (Nginx)
- Put **Nginx** in front of Gunicorn/Waitress to handle HTTPS, static assets, and SSL termination.
- Example Nginx server block:
  ```nginx
  server {
      listen 80;
      server_name saipravesh.yourdomain.org;

      location / {
          proxy_pass http://127.0.0.1:3000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
      }

      client_max_body_size 10M;
  }
  ```

### 3. HTTPS / SSL Certificate
- Obtain a free SSL certificate via **Certbot (Let's Encrypt)**:
  ```bash
  sudo certbot --nginx -d saipravesh.yourdomain.org
  ```

### 4. Database Security & Backups
- Set up a dedicated MySQL database user instead of `root`:
  ```sql
  CREATE USER 'saipravesh_user'@'localhost' IDENTIFIED BY 'StrongPassword123!';
  GRANT ALL PRIVILEGES ON saipravesh.* TO 'saipravesh_user'@'localhost';
  FLUSH PRIVILEGES;
  ```
- Schedule automated daily database backups using `mysqldump` and cron.

### 5. Persistent Uploads Directory
- Ensure the `uploads/` directory has proper write permissions (`chmod 755 uploads`) and is backed up regularly along with the database.

---

## 📁 Repository Structure Map

```
├── app.py              # Main Flask application (Student + Admin API routes)
├── db.py               # MySQL connection pool & SQL query handler
├── admins_config.py    # Environment-based admin authentication configuration
├── schema.sql          # MySQL database schema (Database & 5 Tables creation)
├── requirements.txt    # Python package dependencies
├── .env.example        # Environment variable template
├── test_app.py         # Automated unit test suite
├── index.html          # Student portal UI
├── script.js           # Student portal frontend logic
├── style.css           # Student portal styling
├── admin.html          # Admin portal UI
├── admin.js            # Admin portal frontend logic
├── admin.css           # Admin portal styling
└── uploads/            # Payment receipts and uploaded admin documents
```

---

## 🌸 Sairam & Happy Coding!
