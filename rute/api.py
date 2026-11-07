from flask import Blueprint, request, jsonify
import datetime
from repositori.json_repo import ambil_data, simpan_data
from layanan.ringkasan import hitung_ringkasan_keuangan
from layanan.anggaran import hitung_status_anggaran

api_bp = Blueprint('api', __name__)

@api_bp.route("/<aksi>", methods=["GET", "POST"])
def api(aksi):
    data = ambil_data()
    bulan = request.args.get("bulan", datetime.date.today().strftime("%Y-%m"))
    
    if aksi == "transaksi" and request.method == "GET":
        return jsonify([t for t in data["transaksi"] if t["tanggal"][:7] == bulan])
        
    elif aksi == "transaksi" and request.method == "POST":
        b = request.get_json(silent=True) or {}  
        try:
            datetime.date.fromisoformat(b.get("tanggal", ""))
        except ValueError:
            return jsonify({"error": "Tanggal tidak valid"}), 400
        if not isinstance(b.get("jumlah"), int) or b["jumlah"] <= 0:
            return jsonify({"error": "Jumlah harus bilangan bulat > 0"}), 400
        kat = next((k for k in data["kategori"] if k["nama"] == b.get("kategori")), None)
        if kat is None:
            return jsonify({"error": "Kategori tidak dikenal"}), 400
        if kat["jenis"] != b.get("jenis"):
            return jsonify({"error": "Kategori " + kat["nama"] + " adalah " + kat["jenis"]}), 400
            
        nomor = max([int(t["id"][1:]) for t in data["transaksi"]] + [0]) + 1
        baru = {"id": "T" + str(nomor).zfill(3), "tanggal": b["tanggal"], "jenis": b["jenis"], "kategori": b["kategori"], "jumlah": b["jumlah"], "catatan": b.get("catatan", "")}
        data["transaksi"].append(baru)
        simpan_data(data)
        return jsonify(baru), 201
        
    elif aksi == "hapus" and request.method == "POST":
        id_t = (request.get_json(silent=True) or {}).get("id")
        sisa = [t for t in data["transaksi"] if t["id"] != id_t]
        if len(sisa) == len(data["transaksi"]):
            return jsonify({"error": "Transaksi tidak ditemukan"}), 404
        data["transaksi"] = sisa
        simpan_data(data)
        return jsonify({"dihapus": id_t})
        
    elif aksi == "ringkasan":
        transaksi = [t for t in data["transaksi"] if t["tanggal"][:7] == bulan]
        # Panggil layanan bisnis
        pemasukan, pengeluaran, selisih, rasio = hitung_ringkasan_keuangan(transaksi)
        
        saldo = sum(t["jumlah"] if t["jenis"] == "pemasukan" else -t["jumlah"] for t in data["transaksi"])
        return jsonify({"bulan": bulan, "pemasukan": pemasukan, "pengeluaran": pengeluaran, "selisih": selisih, "rasio_tabungan": rasio, "saldo_total": saldo})
        
    elif aksi == "kategori":
        transaksi = [t for t in data["transaksi"] if t["tanggal"][:7] == bulan and t["jenis"] == "pengeluaran"]
        total = sum(t["jumlah"] for t in transaksi)
        per = {}
        for t in transaksi:
            per[t["kategori"]] = per.get(t["kategori"], 0) + t["jumlah"]
        hasil = [{"kategori": k, "jumlah": v, "persen": round(v / total * 100, 1) if total > 0 else 0} for k, v in per.items()]
        hasil.sort(key=lambda x: x["jumlah"], reverse=True)
        return jsonify(hasil)
        
    elif aksi == "anggaran":
        hasil = []
        for k in data["kategori"]:
            if k["jenis"] == "pengeluaran" and k["anggaran"] > 0:
                terpakai = sum(t["jumlah"] for t in data["transaksi"] if t["tanggal"][:7] == bulan and t["kategori"] == k["nama"] and t["jenis"] == "pengeluaran")
                # Panggil layanan bisnis
                persen, status = hitung_status_anggaran(terpakai, k["anggaran"])
                hasil.append({"kategori": k["nama"], "anggaran": k["anggaran"], "terpakai": terpakai, "sisa": k["anggaran"] - terpakai, "persen": persen, "status": status})
        return jsonify(hasil)
        
    else:
        return jsonify({"error": "Aksi tidak dikenal: " + aksi}), 404
