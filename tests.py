import unittest

from main import app


class TestApiV1(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_1(self):
        response = self.client.get("http://127.0.0.1:8080/api/users/get")
        assert response.status_code == 200 and isinstance(response.json, list)

    def test_2(self):
        response = self.client.get("http://127.0.0.1:8080/api/categories/get")
        assert response.status_code == 200 and isinstance(response.json, list)

    def test_3(self):
        response = self.client.get("http://127.0.0.1:8080/api/forums/get")
        assert response.status_code == 200 and isinstance(response.json, list)

    def test_4(self):
        response = self.client.get("http://127.0.0.1:8080/api/messages/get")
        assert response.status_code == 200 and isinstance(response.json, list)

    def test_5(self):
        response = self.client.get("http://127.0.0.1:8080/api/users/get/1")
        assert response.status_code == 200 and isinstance(response.json, dict)

    def test_6(self):
        response = self.client.get("http://127.0.0.1:8080/api/categories/get/1")
        assert response.status_code == 200 and isinstance(response.json, dict)

    def test_7(self):
        response = self.client.get("http://127.0.0.1:8080/api/forums/get/1")
        assert response.status_code == 200 and isinstance(response.json, dict)

    def test_8(self):
        response = self.client.get("http://127.0.0.1:8080/api/messages/get/1")
        assert response.status_code == 200 and isinstance(response.json, dict)

if __name__ == "__main__":
    unittest.main()
