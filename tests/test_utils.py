import unittest
from utils.format import format_rupiah


class TestFormatRupiah(unittest.TestCase):

    def test_jutaan(self):
        self.assertEqual(format_rupiah(1500000), "Rp 1.500.000")

    def test_ribuan(self):
        self.assertEqual(format_rupiah(1000), "Rp 1.000")

    def test_di_bawah_seribu_tanpa_titik(self):
        self.assertEqual(format_rupiah(999), "Rp 999")

    def test_nol(self):
        self.assertEqual(format_rupiah(0), "Rp 0")

    def test_miliaran(self):
        self.assertEqual(format_rupiah(1000000000), "Rp 1.000.000.000")

    def test_angka_negatif(self):
        self.assertEqual(format_rupiah(-3000), "Rp -3.000")

    def test_input_string_ditolak(self):
        with self.assertRaises(ValueError):
            format_rupiah("abc")

    def test_input_none_ditolak(self):
        with self.assertRaises(TypeError):
            format_rupiah(None)


if __name__ == "__main__":
    unittest.main()