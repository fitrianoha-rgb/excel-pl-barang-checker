# Excel PL vs BARANG Checker

Aplikasi Streamlit untuk membandingkan dua file Excel berdasarkan **urutan baris yang sama**.

## Logika perbandingan

File PL dibandingkan dengan File BARANG pada baris yang sama:

| PL | BARANG |
|---|---|
| MATERIAL CODE | KODE BARANG |
| ITEM NAME | URAIAN |
| QTY | JUMLAH SATUAN |
| N/W / NETTO | NETTO |
| G/W / BRUTO | BRUTO |

Contoh:

- Baris 9 PL dibandingkan dengan baris 9 BARANG.
- Baris 10 PL dibandingkan dengan baris 10 BARANG.
- dan seterusnya.

**Urutan data harus sama.** Program tidak mencari kode yang sama di baris lain.

## Jika semua data cocok

Tidak ada notifikasi keberhasilan yang ditampilkan.

## Jika ada perbedaan

Program menampilkan:

- nomor baris Excel
- field yang berbeda
- nilai dari PL
- nilai dari BARANG

Hasil perbedaan juga dapat di-download sebagai Excel.

## Menjalankan di komputer

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Menjalankan di GitHub

Upload file berikut ke repository:

```text
app.py
requirements.txt
README.md
```

Untuk deploy melalui Streamlit Community Cloud, pilih repository dan file `app.py` sebagai entry point.

## Catatan

Program menormalkan spasi dan line break pada teks, sehingga perbedaan seperti line break atau spasi berlebih tidak dianggap sebagai perbedaan.

Angka dibandingkan dengan toleransi sangat kecil untuk menghindari perbedaan floating-point.
