# PyJen009

งานประจำวันที่ 27 ต.ค. 2569 (Jenkins #4) — โปรแกรมบวกเลขด้วย Python พร้อม CI/CD ด้วย GitHub + Jenkins

push โค้ดขึ้น GitHub แล้ว Jenkins จะ **Build → Test → Deploy** ให้อัตโนมัติ

## โปรแกรม

ใช้แค่ไลบรารีมาตรฐานของ Python ไม่ต้องติดตั้งอะไรเพิ่ม (Python 3.9+)

```bash
python3 calculator.py 2 3          # 2 + 3 = 5
python3 calculator.py 0.1 0.2      # 0.1 + 0.2 = 0.3  (ใช้ Decimal จึงไม่คลาดเคลื่อนแบบ float)
python3 calculator.py              # ถามตัวเลขทีละตัว
python3 app.py                     # หน้าเว็บที่ http://127.0.0.1:8009
```

| ไฟล์ | หน้าที่ |
|---|---|
| `calculator.py` | ฟังก์ชัน `add(a, b)` และโปรแกรมแบบพิมพ์คำสั่ง |
| `app.py` | หน้าเว็บบวกเลข + API `/api/add?a=2&b=3` + `/health` (ใช้ตอน Deploy) |
| `tests/` | เทส 16 ข้อด้วย `unittest` |
| `scripts/deploy.sh` | คัดลอกไป `~/PyJen009-deploy` แล้วเปิดเว็บเวอร์ชันใหม่ที่พอร์ต 8009 |
| `Jenkinsfile` | pipeline 3 stage และเช็ก GitHub ทุก 1 นาที |

## ทดสอบ

```bash
python3 -m unittest discover -s tests -t . -v
```

## CI/CD ด้วย Jenkins

```
แก้โค้ด → git push → GitHub
                       ↓  (Jenkins เช็กทุก 1 นาที: pollSCM)
          Jenkins: Checkout → Build → Test → Deploy
                                              ↓
                                   http://127.0.0.1:8009
```

| Stage | คำสั่ง | ถ้าไม่ผ่าน |
|---|---|---|
| Build | `python3 -m py_compile ...` ตรวจ syntax ทุกไฟล์ และลองรันโปรแกรม | หยุด ไม่เทส ไม่ deploy |
| Test | `python3 -m unittest discover -s tests -t . -v` | หยุด ไม่ deploy |
| Deploy | `scripts/deploy.sh` ปิดเวอร์ชันเก่า เปิดเวอร์ชันใหม่ แล้วเช็ก `/health` | build เป็นสีแดง |

### ตั้งค่า Jenkins

1. ติดตั้งปลั๊กอิน **Git** และ **Pipeline** (มี Python 3 บนเครื่อง Jenkins)
2. New Item → ชื่อ `PyJen009` → **Pipeline**
3. Pipeline → Definition: **Pipeline script from SCM**
   - SCM: Git · Repository URL: `https://github.com/Markrock342/PyJen009.git`
   - Branch: `*/main` · Script Path: `Jenkinsfile`
4. กด **Build Now** หนึ่งครั้ง (Jenkins จะอ่าน `triggers { pollSCM }` จาก Jenkinsfile)
5. หลังจากนั้นทุกครั้งที่ push ขึ้น GitHub, Jenkins จะ build เองภายใน 1 นาที
   หน้า build จะขึ้นว่า **Started by an SCM change**

> ใช้ polling เพราะ Jenkins รันบนเครื่องตัวเอง (localhost) GitHub ส่ง webhook เข้ามาไม่ได้
> ถ้า Jenkins อยู่บนเซิร์ฟเวอร์ที่ GitHub เข้าถึงได้ เปลี่ยนเป็น GitHub webhook ได้
