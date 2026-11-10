#!/usr/bin/env bash
# Deploy: คัดลอกโปรแกรมไปโฟลเดอร์ปลายทาง ปิดเวอร์ชันเก่า แล้วเปิดเวอร์ชันใหม่ที่พอร์ต 8009
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEPLOY_DIR="${DEPLOY_DIR:-$HOME/PyJen009-deploy}"
PORT="${PORT:-8009}"
PYTHON="${PYTHON:-python3}"

echo "Deploy ไปที่ $DEPLOY_DIR (พอร์ต $PORT)"
mkdir -p "$DEPLOY_DIR"
cp "$ROOT/calculator.py" "$ROOT/app.py" "$DEPLOY_DIR/"

# ปิดเวอร์ชันเก่าถ้ายังรันอยู่
if [[ -f "$DEPLOY_DIR/app.pid" ]]; then
  old="$(cat "$DEPLOY_DIR/app.pid" || true)"
  if [[ -n "$old" ]] && kill -0 "$old" 2>/dev/null; then
    kill "$old" || true
    for _ in 1 2 3 4 5; do kill -0 "$old" 2>/dev/null || break; sleep 1; done
  fi
fi

cd "$DEPLOY_DIR"
PORT="$PORT" nohup "$PYTHON" app.py > app.log 2>&1 &
echo $! > app.pid

# รอจนเว็บตอบ แล้วแสดงเวอร์ชันที่ deploy
for _ in $(seq 1 15); do
  if health="$(curl -fsS "http://127.0.0.1:$PORT/health" 2>/dev/null)"; then
    echo "พร้อมใช้งาน: http://127.0.0.1:$PORT  $health"
    exit 0
  fi
  sleep 1
done

echo "เปิดเว็บไม่สำเร็จ ดู log:" >&2
cat app.log >&2
exit 1
