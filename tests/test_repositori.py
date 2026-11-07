import json
import os
import tempfile
import unittest
from unittest.mock import patch

from repositori.json_repo import ambil_data, simpan_data


class TestJsonRepo(unittest.TestCase):
    """Integration test: json_repo + file JSON sementara"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "test_data.json")

        patcher = patch("repositori.json_repo.DATA_FILE", self.path)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_simpan_lalu_ambil(self):
        data = [{"id": 1, "jenis": "pemasukan", "jumlah": 100000}]
        simpan_data(data)
        self.assertEqual(ambil_data(), data)

    def test_simpan_membuat_file(self):
        self.assertFalse(os.path.exists(self.path))
        simpan_data([])
        self.assertTrue(os.path.exists(self.path))

    def test_simpan_menimpa_data_lama(self):
        simpan_data([{"id": 1}])
        simpan_data([{"id": 2}, {"id": 3}])
        self.assertEqual(ambil_data(), [{"id": 2}, {"id": 3}])

    def test_data_kosong(self):
        simpan_data([])
        self.assertEqual(ambil_data(), [])

    def test_karakter_unicode_tidak_diubah(self):
        simpan_data([{"catatan": "Makan siang ☕"}])
        with open(self.path, encoding="utf-8") as f:
            isi_mentah = f.read()
        self.assertIn("☕", isi_mentah)
        self.assertEqual(ambil_data()[0]["catatan"], "Makan siang ☕")

    def test_ambil_file_tidak_ada(self):
        with self.assertRaises(FileNotFoundError):
            ambil_data()

    def test_ambil_json_rusak(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("{ ini bukan json")
        with self.assertRaises(json.JSONDecodeError):
            ambil_data()


if __name__ == "__main__":
    unittest.main()