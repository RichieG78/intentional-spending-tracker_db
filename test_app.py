import os
import tempfile
import unittest

# Force the app to use a local SQLite database for tests before importing app/config.
TEST_DB_PATH = os.path.join(tempfile.gettempdir(), "my_financial_tracker_test.sqlite")
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"
os.environ["SECRET_KEY"] = "test-secret-key"

from app import app, db, User, _hash_password  # noqa: E402


class FlaskAppTests(unittest.TestCase):
    def setUp(self):
        # Prepare a fresh app and empty test data before each test runs.
        app.config.update(TESTING=True)
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        db.session.remove()
        db.drop_all()
        db.create_all()

    # -----------------------------------------------------------------
    # Older syntax example (kept commented on purpose):
    # This duplicate setup method uses older naming and style.
    # def setUp_legacy(self):
    #     app.config.update(TESTING=True)
    #     self.client = app.test_client()
    #     self.app_context = app.app_context()
    #     self.app_context.push()
    #     db.session.remove()
    #     db.drop_all()
    #     db.create_all()

    def tearDown(self):
        # Clean up after each test so one test does not affect another.
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # -----------------------------------------------------------------
    # Older syntax example (kept commented on purpose):
    # This duplicate teardown method shows an older xUnit-style pattern.
    # def tearDown_legacy(self):
    #     db.session.remove()
    #     db.drop_all()
    #     self.app_context.pop()

    def test_about_route_renders(self):
        # Check that the About page opens and shows the app title text.
        response = self.client.get("/about")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Intentional Spending Tracker", response.data)

    # -----------------------------------------------------------------
    # Older syntax example (kept commented on purpose):
    # This duplicate test demonstrates older unittest assertions.
    # def test_about_route_renders_legacy(self):
    #     response = self.client.get("/about")
    #     self.assertEquals(response.status_code, 200)
    #     self.failUnless(b"Intentional Spending Tracker" in response.data)

    def test_dashboard_requires_login(self):
        # Make sure people are sent to login if they try to open Dashboard first.
        response = self.client.get("/dashboard")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers.get("Location", ""))

    # -----------------------------------------------------------------
    # Older syntax example (kept commented on purpose):
    # This duplicate test uses older assertion names for the same checks.
    # def test_dashboard_requires_login_legacy(self):
    #     response = self.client.get("/dashboard")
    #     self.assertEquals(response.status_code, 302)
    #     self.failUnless("/login" in response.headers.get("Location", ""))

    def test_user_insert_post_creates_record(self):
        # Send a new user form and confirm the person is saved.
        payload = {
            "firstname": "Test",
            "lastname": "User",
            "email": "test.user@example.com",
            "password": "demo1234",
        }

        response = self.client.post("/user_insert", json=payload)

        self.assertEqual(response.status_code, 201)
        saved_user = User.query.filter_by(email="test.user@example.com").first()
        self.assertIsNotNone(saved_user)
        # Confirm password safety by checking it is not saved as plain text.
        self.assertNotEqual(saved_user.password, "demo1234")
        self.assertTrue(saved_user.password.startswith("pbkdf2:"))

    # -----------------------------------------------------------------
    # Older syntax example (kept commented on purpose):
    # This duplicate test is intentionally written in older unittest style.
    # def test_user_insert_post_creates_record_legacy(self):
    #     payload = {
    #         "firstname": "Test",
    #         "lastname": "User",
    #         "email": "test.user@example.com",
    #         "password": "demo1234",
    #     }
    #     response = self.client.post("/user_insert", json=payload)
    #     self.assertEquals(response.status_code, 201)
    #     saved_user = User.query.filter_by(email="test.user@example.com").first()
    #     self.failIf(saved_user is None)
    #     self.failIf(saved_user.password == "demo1234")
    #     self.failUnless(saved_user.password.startswith("pbkdf2:"))

    def test_login_post_redirects_to_dashboard_when_credentials_valid(self):
        # Create a person, then check that correct login details open Dashboard.
        user = User(
            firstname="Login",
            lastname="Tester",
            email="login@example.com",
            password=_hash_password("demo1234"),
        )
        db.session.add(user)
        db.session.commit()

        response = self.client.post(
            "/login",
            data={"email": "login@example.com", "password": "demo1234"},
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/dashboard", response.headers.get("Location", ""))

    # -----------------------------------------------------------------
    # Older syntax example (kept commented on purpose):
    # This duplicate test shows legacy assertion naming.
    # def test_login_post_redirects_to_dashboard_when_credentials_valid_legacy(self):
    #     user = User(
    #         firstname="Login",
    #         lastname="Tester",
    #         email="login@example.com",
    #         password=_hash_password("demo1234"),
    #     )
    #     db.session.add(user)
    #     db.session.commit()
    #     response = self.client.post(
    #         "/login",
    #         data={"email": "login@example.com", "password": "demo1234"},
    #         follow_redirects=False,
    #     )
    #     self.assertEquals(response.status_code, 302)
    #     self.failUnless("/dashboard" in response.headers.get("Location", ""))


if __name__ == "__main__":
    unittest.main()
