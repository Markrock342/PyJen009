"""หน้าเว็บโปรแกรมบวกเลข (ใช้ตอน Deploy) — ใช้แค่ไลบรารีมาตรฐานของ Python

เส้นทาง:
    GET /                 หน้าเว็บ กรอกเลขสองตัวแล้วกด "บวก"
    GET /?a=2&b=3         หน้าเว็บพร้อมผลลัพธ์
    GET /api/add?a=2&b=3  {"a": "2", "b": "3", "result": 5}
    GET /health           {"ok": true, "version": "..."}
"""

import html
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from calculator import add, format_number

VERSION = "1.0.0"

PAGE = """<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PyJen009 · โปรแกรมบวกเลข</title>
<style>
  body {{ margin: 0; min-height: 100vh; display: grid; place-items: center; background: #f3f5f9;
         font-family: "Noto Sans Thai Looped", Thonburi, system-ui, sans-serif; color: #111827; }}
  main {{ width: min(440px, calc(100% - 2rem)); padding: 2rem; border-radius: 16px; background: #fff;
          border: 1px solid #e1e5ec; }}
  h1 {{ margin: 0 0 .25rem; font-size: 1.6rem; }}
  p.sub {{ margin: 0 0 1.5rem; color: #4b5563; }}
  form {{ display: grid; grid-template-columns: 1fr auto 1fr; gap: .6rem; align-items: center; }}
  input {{ width: 100%; box-sizing: border-box; padding: .7rem; font: inherit; font-size: 1.2rem;
           border: 1.5px solid #c3c9d4; border-radius: 10px; text-align: center; }}
  input:focus {{ outline: none; border-color: #2563eb; box-shadow: 0 0 0 3px #dbe6ff; }}
  .plus {{ font-size: 1.5rem; font-weight: 700; }}
  button {{ grid-column: 1 / -1; padding: .8rem; font: inherit; font-size: 1.1rem; font-weight: 600;
            color: #fff; background: #2563eb; border: 0; border-radius: 10px; cursor: pointer; }}
  button:hover {{ background: #1d4ed8; }}
  .result {{ margin-top: 1.25rem; padding: 1rem; border-radius: 12px; background: #eef4ff; text-align: center;
             font-size: 1.5rem; font-weight: 700; }}
  .error {{ margin-top: 1.25rem; padding: .8rem 1rem; border-radius: 12px; background: #fdeeec; color: #b42318; }}
  footer {{ margin-top: 1.5rem; color: #6b7280; font-size: .85rem; }}
</style>
</head>
<body>
<main>
  <h1>โปรแกรมบวกเลข</h1>
  <p class="sub">กรอกตัวเลขสองจำนวน แล้วกด “บวก”</p>
  <form method="get" action="/">
    <input name="a" inputmode="decimal" aria-label="ตัวเลขที่ 1" value="{a}" required>
    <span class="plus" aria-hidden="true">+</span>
    <input name="b" inputmode="decimal" aria-label="ตัวเลขที่ 2" value="{b}" required>
    <button type="submit">บวก</button>
  </form>
  {output}
  <footer>PyJen009 · เวอร์ชัน {version} · deploy โดย Jenkins</footer>
</main>
</body>
</html>"""


def calculate(params):
    """คืน (สถานะ HTTP, ข้อมูล) จาก query string"""
    a = params.get("a", [""])[0]
    b = params.get("b", [""])[0]
    try:
        return 200, {"a": a, "b": b, "result": add(a, b)}
    except ValueError as error:
        return 400, {"a": a, "b": b, "error": str(error)}


class Handler(BaseHTTPRequestHandler):
    server_version = f"PyJen009/{VERSION}"

    def send(self, status, body, content_type):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, status, payload):
        self.send(status, json.dumps(payload, ensure_ascii=False), "application/json")

    def do_GET(self):
        url = urlparse(self.path)
        params = parse_qs(url.query)

        if url.path == "/health":
            self.send_json(200, {"ok": True, "service": "PyJen009", "version": VERSION})
        elif url.path == "/api/add":
            status, payload = calculate(params)
            self.send_json(status, payload)
        elif url.path == "/":
            output = ""
            if "a" in params or "b" in params:
                status, payload = calculate(params)
                if status == 200:
                    output = (
                        f'<p class="result" role="status">{html.escape(payload["a"])} + '
                        f'{html.escape(payload["b"])} = {format_number(payload["result"])}</p>'
                    )
                else:
                    output = f'<p class="error" role="alert">{html.escape(payload["error"])}</p>'
            page = PAGE.format(
                a=html.escape(params.get("a", [""])[0]),
                b=html.escape(params.get("b", [""])[0]),
                output=output,
                version=VERSION,
            )
            self.send(200, page, "text/html")
        else:
            self.send_json(404, {"error": "ไม่พบหน้านี้"})

    def log_message(self, fmt, *args):  # ลด log ให้อ่านง่าย
        print(f"{self.address_string()} {fmt % args}")


def make_server(port, host="127.0.0.1"):
    return ThreadingHTTPServer((host, port), Handler)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8009"))
    server = make_server(port)
    print(f"PyJen009 v{VERSION} พร้อมใช้งานที่ http://127.0.0.1:{port}")
    server.serve_forever()
