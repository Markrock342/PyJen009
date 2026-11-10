import io
import unittest
from contextlib import redirect_stdout

from calculator import add, add_many, format_number, main, to_number


class TestAdd(unittest.TestCase):
    def test_add_integers(self):
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add(-4, 4), 0)
        self.assertEqual(add(1_000_000, 1), 1_000_001)

    def test_add_decimals_exactly(self):
        # 0.1 + 0.2 ใน float ปกติได้ 0.30000000000000004 แต่โปรแกรมนี้ต้องได้ 0.3
        self.assertEqual(add(0.1, 0.2), 0.3)
        self.assertEqual(add("1.5", "2.25"), 3.75)

    def test_result_type(self):
        self.assertIsInstance(add("2.5", "2.5"), int)
        self.assertIsInstance(add("2.5", "1"), float)

    def test_add_text_numbers(self):
        self.assertEqual(add("10", " 20 "), 30)
        self.assertEqual(add("1,000", "234"), 1234)
        self.assertEqual(add("-7", "2"), -5)

    def test_reject_invalid_input(self):
        for bad in ["abc", "", "   ", "1+1", None, True, "nan", "inf"]:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    add(bad, 1)

    def test_to_number_message_is_thai(self):
        with self.assertRaisesRegex(ValueError, "ไม่ใช่ตัวเลข"):
            to_number("สิบ")


class TestAddMany(unittest.TestCase):
    def test_add_many_numbers(self):
        self.assertEqual(add_many(1, 2, 3, 4), 10)
        self.assertEqual(add_many("0.1", "0.2", "0.3"), 0.6)

    def test_add_many_needs_two_numbers(self):
        with self.assertRaises(ValueError):
            add_many(5)


class TestFormat(unittest.TestCase):
    def test_format_number(self):
        self.assertEqual(format_number(1234567), "1,234,567")
        self.assertEqual(format_number(1234.5), "1,234.5")
        self.assertEqual(format_number(0.3), "0.3")


class TestCli(unittest.TestCase):
    def run_cli(self, args):
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(args)
        return code, out.getvalue().strip()

    def test_cli_adds_two_numbers(self):
        self.assertEqual(self.run_cli(["2", "3"]), (0, "2 + 3 = 5"))

    def test_cli_reports_error(self):
        code, output = self.run_cli(["2", "x"])
        self.assertEqual(code, 1)
        self.assertIn("ผิดพลาด", output)

    def test_cli_adds_many_numbers(self):
        self.assertEqual(self.run_cli(["1", "2", "3", "4"]), (0, "1 + 2 + 3 + 4 = 10"))

    def test_cli_usage_with_wrong_argument_count(self):
        code, output = self.run_cli(["1"])
        self.assertEqual(code, 2)
        self.assertIn("ใช้งาน", output)


if __name__ == "__main__":
    unittest.main()
