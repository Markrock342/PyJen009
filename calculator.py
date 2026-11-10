"""โปรแกรมบวกเลขอย่างง่าย

ใช้งาน:
    python3 calculator.py 2 3        -> 2 + 3 = 5
    python3 calculator.py 1 2 3 4    -> 1 + 2 + 3 + 4 = 10
    python3 calculator.py            -> ถามตัวเลขทีละตัว
"""

import sys
from decimal import Decimal, InvalidOperation


def to_number(value):
    """แปลงค่าที่รับมา (ตัวเลขหรือข้อความ) เป็น Decimal เพื่อให้บวกทศนิยมได้แม่นยำ"""
    if isinstance(value, bool):
        raise ValueError("ต้องเป็นตัวเลข ไม่ใช่ True/False")
    if isinstance(value, (int, float, Decimal)):
        number = Decimal(str(value))
    else:
        text = str(value).strip().replace(",", "")
        if not text:
            raise ValueError("กรุณากรอกตัวเลข")
        try:
            number = Decimal(text)
        except InvalidOperation:
            raise ValueError(f"'{value}' ไม่ใช่ตัวเลข") from None
    if not number.is_finite():
        raise ValueError("ตัวเลขต้องเป็นค่าจำกัด")
    return number


def add(a, b):
    """บวกเลขสองจำนวน คืนค่าเป็น int ถ้าผลลัพธ์เป็นจำนวนเต็ม ไม่อย่างนั้นคืน float"""
    total = to_number(a) + to_number(b)
    if total == total.to_integral_value():
        return int(total)
    return float(total)


def add_many(*values):
    """บวกเลขหลายจำนวน ต้องมีอย่างน้อย 2 จำนวน"""
    if len(values) < 2:
        raise ValueError("ต้องมีตัวเลขอย่างน้อย 2 จำนวน")
    total = 0
    for value in values:
        total = add(total, value)
    return total


def format_number(value):
    """แสดงผลตัวเลขให้อ่านง่าย เช่น 1234.5 -> 1,234.5"""
    if isinstance(value, int):
        return f"{value:,}"
    return f"{value:,.10f}".rstrip("0").rstrip(".")


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    try:
        if len(args) >= 2:
            numbers = args
        elif not args:
            numbers = [input("ตัวเลขที่ 1: "), input("ตัวเลขที่ 2: ")]
        else:
            print("ใช้งาน: python3 calculator.py <ตัวเลข1> <ตัวเลข2> [ตัวเลขอื่น ๆ ...]")
            return 2
        result = add_many(*numbers)
    except ValueError as error:
        print(f"ผิดพลาด: {error}")
        return 1
    expression = " + ".join(f"{to_number(n).normalize():f}" for n in numbers)
    print(f"{expression} = {format_number(result)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
