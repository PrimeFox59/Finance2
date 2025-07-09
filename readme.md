# 📒 Aplikasi Keuangan Berbasis Streamlit + Google Sheets

Aplikasi web sederhana untuk pencatatan income dan outcome menggunakan **Streamlit** dan **Google Sheets** sebagai backend. Aplikasi ini mendukung multi-user, filter data, visualisasi income vs outcome, serta grafik pie dan bar interaktif.

---

## 🚀 Fitur Utama

- Input data income/outcome per pengguna
- Tambah kategori transaksi baru
- Riwayat transaksi per pengguna (dengan filter bulan & tahun)
- Visualisasi pengeluaran dalam bentuk **Pie Chart**
- Perbandingan harian income vs outcome (**Bar Chart**)
- Rekapitulasi income & outcome per pengguna (**Bar Chart**)
- Tren bulanan income dan outcome (**Line Chart**)
- Tabel lengkap semua transaksi pengguna

---

## 🧰 Teknologi yang Digunakan

- [Streamlit](https://streamlit.io/)
- [Google Sheets API (gspread)](https://gspread.readthedocs.io/)
- [oauth2client](https://pypi.org/project/oauth2client/)
- [Altair](https://altair-viz.github.io/)
- [Pandas](https://pandas.pydata.org/)

---

## 📂 Struktur File
.
├── app.py # File utama Streamlit
├── credentials.json # File service account Google Sheets
├── requirements.txt
└── README.md



---

## 🔐 Persiapan Google Sheets API

1. Buat [Google Cloud Project](https://console.cloud.google.com/)
2. Aktifkan **Google Sheets API**
3. Buat **Service Account** dan unduh `credentials.json`
4. Share Google Sheet kamu dengan email dari service account (edit access)

---

## ▶️ Menjalankan Aplikasi

```bash
pip install -r requirements.txt
streamlit run app.py
