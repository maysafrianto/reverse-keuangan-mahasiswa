import json
import os
import tempfile
import unittest
from unittest.mock import patch

from app import create_app

DATA_PALSU = {
    "transaksi": [
        {"id": "T001", "tanggal": "2026-11-05", "jenis": "pemasukan",
         "kategori": "Uang Saku", "jumlah": 1000000},
        {"id": "T002", "tanggal": "2026-11-06", "jenis": "pengeluaran",
         "kategori": "Makanan", "jumlah": 150000},
        {"id": "T003", "tanggal": "2026-10-20", "jenis": "pengeluaran",
         "kategori": "Makanan", "jumlah": 50000},
    ],
    "kategori": [
        {"nama": "Uang Saku", "jenis": "pemasukan", "anggaran": 0},
        {"nama": "Makanan", "jenis": "pengeluaran", "anggaran": 200000},
    ],
}

POST_VALID = {
    "tanggal": "2026-11-10",
    "jenis": "pengeluaran",
    "kategori": "Makanan",
    "jumlah": 25000,
}


class TestRuteBase(unittest.TestCase):
    """Menyiapkan file data sementara dan test client untuk semua test rute."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "test_data.json")
        self.tulis_data(DATA_PALSU)

        patcher = patch("repositori.json_repo.DATA_FILE", self.path)
        patcher.start()
        self.addCleanup(patcher.stop)

        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()

    def tulis_data(self, data):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    def jumlah_transaksi(self, bulan):
        res = self.client.get(f"/api/transaksi?bulan={bulan}")
        return len(res.get_json())


class TestApiGet(TestRuteBase):

    def test_get_transaksi_per_bulan(self):
        res = self.client.get("/api/transaksi?bulan=2026-11")
        self.assertEqual(res.status_code, 200)
        ids = [t["id"] for t in res.get_json()]
        self.assertEqual(ids, ["T001", "T002"])

    def test_get_transaksi_bulan_lain(self):
        res = self.client.get("/api/transaksi?bulan=2026-10")
        self.assertEqual([t["id"] for t in res.get_json()], ["T003"])

    def test_get_transaksi_bulan_kosong(self):
        res = self.client.get("/api/transaksi?bulan=2025-01")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json(), [])


class TestApiPost(TestRuteBase):

    def test_post_valid(self):
        res = self.client.post("/api/transaksi", json=POST_VALID)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.get_json()["id"], "T004")  # lanjut dari T003

    def test_post_valid_tersimpan(self):
        self.assertEqual(self.jumlah_transaksi("2026-11"), 2)
        self.client.post("/api/transaksi", json=POST_VALID)
        self.assertEqual(self.jumlah_transaksi("2026-11"), 3)

    def test_post_tanggal_tidak_valid(self):
        body = dict(POST_VALID, tanggal="bukan-tanggal")
        res = self.client.post("/api/transaksi", json=body)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.get_json()["error"], "Tanggal tidak valid")

    def test_post_jumlah_nol(self):
        body = dict(POST_VALID, jumlah=0)
        res = self.client.post("/api/transaksi", json=body)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.get_json()["error"], "Jumlah harus bilangan bulat > 0")

    def test_post_jumlah_bukan_angka(self):
        body = dict(POST_VALID, jumlah="25000")
        res = self.client.post("/api/transaksi", json=body)
        self.assertEqual(res.status_code, 400)

    def test_post_kategori_tidak_dikenal(self):
        body = dict(POST_VALID, kategori="Tidak Ada")
        res = self.client.post("/api/transaksi", json=body)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.get_json()["error"], "Kategori tidak dikenal")

    def test_post_jenis_tidak_cocok_kategori(self):
        body = dict(POST_VALID, jenis="pemasukan")  # Makanan itu pengeluaran
        res = self.client.post("/api/transaksi", json=body)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.get_json()["error"], "Kategori Makanan adalah pengeluaran")

    def test_post_ditolak_tidak_mengubah_data(self):
        self.client.post("/api/transaksi", json=dict(POST_VALID, jumlah=-5))
        self.assertEqual(self.jumlah_transaksi("2026-11"), 2)


class TestHalamanWeb(TestRuteBase):

    def test_halaman_utama(self):
        res = self.client.get("/?bulan=2026-11")
        self.assertEqual(res.status_code, 200)

    def test_halaman_utama_bulan_tanpa_data(self):
        res = self.client.get("/?bulan=2025-01")
        self.assertEqual(res.status_code, 200)


if __name__ == "__main__":
    unittest.main()