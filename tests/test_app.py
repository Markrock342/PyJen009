import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen

from app import VERSION, make_server


class TestWebApp(unittest.TestCase):
    """เปิดเว็บเซิร์ฟเวอร์จริงบนพอร์ตว่าง แล้วยิงคำขอ HTTP เข้าไป"""

    @classmethod
    def setUpClass(cls):
        cls.server = make_server(0)
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def get(self, path):
        try:
            with urlopen(self.base + path, timeout=5) as res:
                return res.status, res.read().decode("utf-8")
        except HTTPError as error:
            with error:
                return error.code, error.read().decode("utf-8")

    def test_health(self):
        status, body = self.get("/health")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {"ok": True, "service": "PyJen009", "version": VERSION})

    def test_api_add(self):
        status, body = self.get("/api/add?a=2&b=3")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["result"], 5)

    def test_api_rejects_bad_number(self):
        status, body = self.get("/api/add?a=2&b=hello")
        self.assertEqual(status, 400)
        self.assertIn("ไม่ใช่ตัวเลข", json.loads(body)["error"])

    def test_page_shows_form_and_result(self):
        status, body = self.get("/?a=10&b=20")
        self.assertEqual(status, 200)
        self.assertIn("<form", body)
        self.assertIn("10 + 20 = 30", body)
        self.assertIn(f"เวอร์ชัน {VERSION}", body)

    def test_page_escapes_user_input(self):
        status, body = self.get("/?a=%3Cscript%3E&b=1")
        self.assertEqual(status, 200)
        self.assertNotIn("<script>", body)
        self.assertIn("&lt;script&gt;", body)

    def test_unknown_path(self):
        status, _ = self.get("/nope")
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
