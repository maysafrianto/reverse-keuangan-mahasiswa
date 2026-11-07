import os

# Ngambil path folder utama dompet-keuangan
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")

RASIO_IDEAL = 20
RASIO_DEFISIT = 0
RASIO_KRITIS = 10

ANGGARAN_WASPADA = 75
ANGGARAN_MELEBIHI = 100
