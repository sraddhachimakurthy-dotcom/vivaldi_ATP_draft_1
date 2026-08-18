import io
import os
import unittest
from unittest.mock import patch, MagicMock

# Set env before importing app
os.environ["SESSION_SECRET"] = "test_secret_key"
os.environ["ADMIN_1"] = "admin:pass123:superadmin:Super Admin"
os.environ["ADMIN_2"] = "director1:pass123:director:Director User"
os.environ["ADMIN_3"] = "staff1:pass123:staff:Staff User"

import app as flask_app


class TestStudentRoutes(unittest.TestCase):
    def setUp(self):
        flask_app.app.config["TESTING"] = True
        self.client = flask_app.app.test_client()

    @patch("db.query")
    def test_application_start_success(self, mock_query):
        mock_query.side_effect = [
            [],
            (10, 1),
            (100, 1)
        ]
        response = self.client.post("/application/start", json={
            "application_number": "APP123",
            "candidate_name": "John Doe",
            "email": "john@example.com",
            "mobile": "1234567890",
            "dob": "2000-01-01",
            "category": "General"
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("application_id"), 100)

    @patch("db.query")
    def test_application_start_existing(self, mock_query):
        mock_query.side_effect = [
            [{"id": 10}],
            [{"id": 100}]
        ]
        response = self.client.post("/application/start", json={
            "application_number": "APP123",
            "candidate_name": "John Doe"
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("application_id"), 100)
        self.assertTrue(data.get("resumed"))

    def test_application_start_missing_fields(self):
        response = self.client.post("/application/start", json={})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("error", data)

    @patch("db.query")
    def test_application_course_success(self, mock_query):
        mock_query.return_value = (0, 1)
        response = self.client.post("/application/course", json={
            "application_id": 100,
            "course_level": "Undergraduate",
            "course_name": "B.Sc. Computer Science"
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get("success"))

    def test_application_course_missing_fields(self):
        response = self.client.post("/application/course", json={"application_id": 100})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("error", data)

    @patch("db.query")
    @patch("app.save_upload")
    def test_payment_upload_success(self, mock_save_upload, mock_query):
        mock_save_upload.return_value = "12345_test.png"
        mock_query.return_value = (0, 1)

        data = {
            "application_id": "100",
            "payment_file": (io.BytesIO(b"fake image data"), "test.png")
        }
        response = self.client.post("/payment/upload", data=data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 200)
        res_data = response.get_json()
        self.assertTrue(res_data.get("success"))
        self.assertEqual(res_data.get("filename"), "12345_test.png")

    @patch("db.query")
    def test_health_record_success(self, mock_query):
        mock_query.return_value = (0, 1)
        response = self.client.post("/health", json={
            "application_id": 100,
            "age": "20",
            "height": "175",
            "weight": "68",
            "bloodGroup": "O+",
            "asthma": "No"
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get("success"))

    def test_health_record_missing_app_id(self):
        response = self.client.post("/health", json={})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("error", data)

    @patch("db.query")
    def test_application_status(self, mock_query):
        mock_query.return_value = [{
            "status": "Completed",
            "id": 100,
            "full_name": "John Doe",
            "course_name": "B.Sc. Computer Science"
        }]
        response = self.client.get("/application/status/APP123")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "Completed")

    @patch("db.query")
    def test_forms_list(self, mock_query):
        mock_query.return_value = [{"id": 1, "doc_name": "Form A", "filename": "forma.pdf"}]
        response = self.client.get("/forms")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)


class TestAdminRoutes(unittest.TestCase):
    def setUp(self):
        flask_app.app.config["TESTING"] = True
        self.client = flask_app.app.test_client()

    def test_admin_login_success(self):
        response = self.client.post("/admin/login", json={
            "username": "admin",
            "password": "pass123"
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("role"), "superadmin")

    def test_admin_login_failure(self):
        response = self.client.post("/admin/login", json={
            "username": "admin",
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data.get("success"))

    def test_admin_me_unauthorized(self):
        response = self.client.get("/admin/me")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data.get("loggedIn"))

    def test_admin_me_authorized(self):
        with self.client.session_transaction() as sess:
            sess["admin"] = True
            sess["role"] = "superadmin"
            sess["name"] = "Super Admin"
        response = self.client.get("/admin/me")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get("loggedIn"))
        self.assertEqual(data.get("role"), "superadmin")

    @patch("db.query")
    def test_admin_applications_unauthorized(self, mock_query):
        response = self.client.get("/admin/applications")
        self.assertEqual(response.status_code, 403)

    @patch("db.query")
    def test_admin_applications_authorized(self, mock_query):
        mock_query.return_value = [{"id": 1, "full_name": "Alice"}]
        with self.client.session_transaction() as sess:
            sess["admin"] = True
            sess["role"] = "staff"
        response = self.client.get("/admin/applications")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)

    @patch("db.query")
    def test_admin_stats(self, mock_query):
        mock_query.return_value = [{"total": 10, "started": 2, "completed": 5, "approved": 3, "rejected": 0, "locked": 0}]
        with self.client.session_transaction() as sess:
            sess["admin"] = True
            sess["role"] = "director"
        response = self.client.get("/admin/stats")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("total"), 10)

    @patch("db.query")
    def test_admin_status_update_staff_permitted(self, mock_query):
        mock_query.return_value = (0, 1)
        with self.client.session_transaction() as sess:
            sess["admin"] = True
            sess["role"] = "staff"
        response = self.client.post("/admin/status", json={"id": 1, "status": "Completed"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get("success"))

    @patch("db.query")
    def test_admin_status_update_staff_forbidden(self, mock_query):
        with self.client.session_transaction() as sess:
            sess["admin"] = True
            sess["role"] = "staff"
        response = self.client.post("/admin/status", json={"id": 1, "status": "Approved"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("error", data)

    @patch("db.query")
    def test_admin_lock_superadmin_only(self, mock_query):
        mock_query.return_value = (0, 1)
        with self.client.session_transaction() as sess:
            sess["admin"] = True
            sess["role"] = "director"
        response = self.client.post("/admin/lock", json={"id": 1})
        self.assertEqual(response.status_code, 403)

        with self.client.session_transaction() as sess:
            sess["admin"] = True
            sess["role"] = "superadmin"
        response = self.client.post("/admin/lock", json={"id": 1})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get("success"))


if __name__ == "__main__":
    unittest.main()
