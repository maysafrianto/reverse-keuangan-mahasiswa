import unittest
from layanan.anggaran import hitung_status_anggaran
from layanan.ringkasan import hitung_ringkasan_keuangan, tentukan_nasihat


class TestAnggaranBatas(unittest.TestCase):

    def test_persen_dan_status_aman(self):
        self.assertEqual(hitung_status_anggaran(10000, 200000), (5.0, "aman"))

    def test_nol_terpakai(self):
        self.assertEqual(hitung_status_anggaran(0, 200000), (0.0, "aman"))

    def test_batas_waspada(self):
        # tepat 75% -> waspada (memakai >=)
        self.assertEqual(hitung_status_anggaran(150000, 200000), (75.0, "waspada"))

    def test_tepat_100_persen_masih_waspada(self):
        # melebihi memakai >, jadi 100% belum dianggap melebihi
        self.assertEqual(hitung_status_anggaran(200000, 200000), (100.0, "waspada"))

    def test_melebihi(self):
        self.assertEqual(hitung_status_anggaran(250000, 200000), (125.0, "melebihi"))

    def test_anggaran_nol(self):
        with self.assertRaises(ZeroDivisionError):
            hitung_status_anggaran(1000, 0)


class TestRingkasan(unittest.TestCase):

    def test_ringkasan_normal(self):
        data = [
            {"jenis": "pemasukan", "jumlah": 1000000},
            {"jenis": "pengeluaran", "jumlah": 600000},
        ]
        hasil = hitung_ringkasan_keuangan(data)
        self.assertEqual(hasil, (1000000, 600000, 400000, 40.0))

    def test_ringkasan_pembulatan(self):
        data = [
            {"jenis": "pemasukan", "jumlah": 300000},
            {"jenis": "pengeluaran", "jumlah": 200000},
        ]
        _, _, _, rasio = hitung_ringkasan_keuangan(data)
        self.assertEqual(rasio, 33.3)

    def test_ringkasan_data_kosong(self):
        self.assertEqual(hitung_ringkasan_keuangan([]), (0, 0, 0, 0))

    def test_ringkasan_tanpa_pemasukan(self):
        data = [{"jenis": "pengeluaran", "jumlah": 50000}]
        hasil = hitung_ringkasan_keuangan(data)
        self.assertEqual(hasil, (0, 50000, -50000, 0))


class TestNasihat(unittest.TestCase):

    def test_tanpa_pemasukan(self):
        self.assertIn("Belum ada pemasukan", tentukan_nasihat(0, 0))

    def test_defisit(self):
        self.assertIn("melebihi", tentukan_nasihat(1000000, -5))

    def test_kritis(self):
        self.assertIn("di bawah 10%", tentukan_nasihat(1000000, 5))

    def test_cukup_baik(self):
        self.assertIn("Cukup baik", tentukan_nasihat(1000000, 15))

    def test_hebat(self):
        self.assertIn("Hebat", tentukan_nasihat(1000000, 25))


if __name__ == "__main__":
    unittest.main()