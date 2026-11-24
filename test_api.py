"""
Automated Integration and API Tests for Student Management System.
Tests all CRUD operations, validations, and edge cases.
"""

import sys
import os
import unittest

# Ensure project and backend directories are in python path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "backend"))

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import get_db
from backend.app.crud import seed_sample_students

# Ensure sample data is seeded for tests
db = next(get_db())
try:
    seed_sample_students(db)
finally:
    db.close()

client = TestClient(app)



class TestStudentManagementAPI(unittest.TestCase):

    def test_01_health_check(self):
        """Verify health check endpoint returns 200 OK."""
        res = client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")

    def test_02_get_initial_students(self):
        """Verify initial seeded students are returned."""
        res = client.get("/api/students")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0, "Initial student list should have seeded records")

    def test_03_create_new_student(self):
        """Test registering a new student with valid data."""
        payload = {
            "usn": "1TEST99CS999",
            "name": "Integration Test Student",
            "email": "teststudent@example.com",
            "phone": "9199887766",
            "department": "Computer Science",
            "semester": 5,
            "gender": "Female"
        }
        res = client.post("/api/students", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["usn"], "1TEST99CS999")
        self.assertEqual(data["name"], "Integration Test Student")
        self.assertIn("id", data)

    def test_04_duplicate_usn_fails(self):
        """Test that registering duplicate USN returns 400 Bad Request."""
        payload = {
            "usn": "1TEST99CS999",
            "name": "Duplicate Student",
            "email": "duplicate@example.com",
            "phone": "9123456789",
            "department": "Information Science",
            "semester": 3,
            "gender": "Male"
        }
        res = client.post("/api/students", json=payload)
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertIn("already exists", data["detail"])

    def test_05_search_student_by_name_and_usn(self):
        """Test search query parameter filtering."""
        # Search by USN
        res = client.get("/api/students?search=1TEST99CS999")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(len(data), 1)
        self.assertEqual(data[0]["usn"], "1TEST99CS999")

        # Search by partial Name
        res_name = client.get("/api/students?search=Integration")
        self.assertEqual(res_name.status_code, 200)
        data_name = res_name.json()
        self.assertGreaterEqual(len(data_name), 1)

    def test_06_filter_by_department(self):
        """Test filtering by academic department."""
        res = client.get("/api/students?department=Computer Science")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        for s in data:
            self.assertEqual(s["department"], "Computer Science")

    def test_07_update_student(self):
        """Test updating an existing student."""
        # First find the test student
        res_find = client.get("/api/students?search=1TEST99CS999")
        student = res_find.json()[0]
        student_id = student["id"]

        update_payload = {
            "name": "Updated Test Student",
            "semester": 6
        }
        res_update = client.put(f"/api/students/{student_id}", json=update_payload)
        self.assertEqual(res_update.status_code, 200)
        updated_data = res_update.json()
        self.assertEqual(updated_data["name"], "Updated Test Student")
        self.assertEqual(updated_data["semester"], 6)

    def test_08_delete_student(self):
        """Test deleting a student record."""
        # Find test student
        res_find = client.get("/api/students?search=1TEST99CS999")
        student = res_find.json()[0]
        student_id = student["id"]

        # Delete
        res_del = client.delete(f"/api/students/{student_id}")
        self.assertEqual(res_del.status_code, 200)

        # Confirm 404 on get
        res_confirm = client.get(f"/api/students/{student_id}")
        self.assertEqual(res_confirm.status_code, 404)

    def test_09_dashboard_stats(self):
        """Test dashboard statistics endpoint."""
        res = client.get("/api/stats")
        self.assertEqual(res.status_code, 200)
        stats = res.json()
        self.assertIn("total_students", stats)
        self.assertIn("departments_count", stats)
        self.assertIn("department_distribution", stats)
        self.assertIn("semester_distribution", stats)


if __name__ == "__main__":
    unittest.main()
