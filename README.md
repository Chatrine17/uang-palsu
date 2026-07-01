# Dashboard UPUR — KPw Bank Indonesia Kota Pematang Siantar

Dashboard interaktif untuk memantau temuan UPUR (Uang Palsu & Uang Rusak) periode 2018–2025.

## Struktur Project

```
.
├── app.py                          # Aplikasi Streamlit (dashboard)
├── requirements.txt                # Dependency Python
├── uipur_parsing_eda.ipynb         # Notebook Colab: parsing data mentah + EDA
└── data/
    ├── uipur_2019-2025.xlsx        # Data mentah (pivot table export)
    ├── yearly_totals.csv           # Hasil olahan: ringkasan per tahun
    └── palsu_by_tahun_emisi.csv    # Hasil olahan: breakdown Palsu per tahun emisi
```

## Cara Kerja

1. **Notebook (`uipur_parsing_eda.ipynb`)** dijalankan di Google Colab untuk:
   - Membaca file Excel pivot table mentah (struktur berbeda tiap tahun)
   - Membersihkan & menyusun ulang menjadi data tidy
   - Menghasilkan `yearly_totals.csv` dan `palsu_by_tahun_emisi.csv`
   - Melakukan EDA singkat (tren, komposisi kategori, breakdown tahun emisi)

2. **`app.py`** membaca kedua CSV hasil olahan tersebut dan menampilkannya sebagai
   dashboard interaktif (filter rentang tahun, KPI cards, tren, komposisi kategori,
   drill-down per tahun emisi uang).

## Cara Menjalankan

### Lokal
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Deploy ke Streamlit Community Cloud
1. Push seluruh folder ini ke repo GitHub
2. Buka [share.streamlit.io](https://share.streamlit.io), hubungkan ke repo
3. Set **Main file path** ke `app.py`
4. Deploy

## Update Data

Jika ada data UPUR tahun baru:
1. Tambahkan ke file Excel mentah, lalu jalankan ulang `uipur_parsing_eda.ipynb` di Colab
2. Download ulang `yearly_totals.csv` dan `palsu_by_tahun_emisi.csv`
3. Replace file di folder `data/`, commit & push — dashboard otomatis terupdate

## Catatan

- Breakdown "Tahun Emisi" baru tersedia mulai data 2020 (data 2018–2019 hanya
  punya total kategori, tanpa rincian tahun emisi).
