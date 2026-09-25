import streamlit as st
import pandas as pd
import numpy as np
import io

st.set_page_config(page_title="PL vs BARANG Checker", page_icon="📊", layout="wide")

st.title("📊 Excel PL vs BARANG Checker")
st.caption("Perbandingan dilakukan berdasarkan URUTAN BARIS. Baris PL dibandingkan dengan baris BARANG pada posisi yang sama.")

def normalize_text(value):
    if pd.isna(value):
        return ""
    return " ".join(str(value).replace("\n", " ").replace("\r", " ").split()).strip().upper()

def normalize_number(value):
    if pd.isna(value) or value == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return normalize_text(value)

def values_equal(a, b, tolerance=0.000001):
    na = normalize_number(a)
    nb = normalize_number(b)

    if na is None and nb is None:
        return True

    if isinstance(na, (int, float)) and isinstance(nb, (int, float)):
        return abs(na - nb) <= tolerance

    return normalize_text(a) == normalize_text(b)

def find_column(df, candidates):
    normalized = {normalize_text(c): c for c in df.columns}
    for candidate in candidates:
        key = normalize_text(candidate)
        if key in normalized:
            return normalized[key]
    return None

def read_excel(uploaded_file):
    return pd.read_excel(uploaded_file, sheet_name=None)

def compare_files(pl_file, barang_file, pl_sheet, barang_sheet):
    pl_sheets = read_excel(pl_file)
    barang_sheets = read_excel(barang_file)

    pl = pl_sheets[pl_sheet]
    barang = barang_sheets[barang_sheet]

    # Kolom PL
    pl_material = find_column(pl, ["MATERIAL CODE", "MATERIAL\nCODE", "MATERIALCODE"])
    pl_item = find_column(pl, ["ITEM NAME", "ITEM\nNAME", "ITEMNAME"])
    pl_qty = find_column(pl, ["QTY"])
    pl_netto = find_column(pl, ["N/W", "NW", "NETTO", "N/W KG"])
    pl_bruto = find_column(pl, ["G/W", "GW", "BRUTO", "G/W KG"])

    # Kolom BARANG
    barang_kode = find_column(barang, ["KODE BARANG", "KODEBARANG"])
    barang_uraian = find_column(barang, ["URAIAN"])
    barang_qty = find_column(barang, ["JUMLAH SATUAN", "JUMLAHSATUAN", "QTY"])
    barang_netto = find_column(barang, ["NETTO"])
    barang_bruto = find_column(barang, ["BRUTO"])

    missing = []
    for label, col in {
        "PL - MATERIAL CODE": pl_material,
        "PL - ITEM NAME": pl_item,
        "PL - QTY": pl_qty,
        "PL - NETTO/NW": pl_netto,
        "PL - BRUTO/GW": pl_bruto,
        "BARANG - KODE BARANG": barang_kode,
        "BARANG - URAIAN": barang_uraian,
        "BARANG - JUMLAH SATUAN": barang_qty,
        "BARANG - NETTO": barang_netto,
        "BARANG - BRUTO": barang_bruto,
    }.items():
        if col is None:
            missing.append(label)

    if missing:
        raise ValueError("Kolom berikut tidak ditemukan: " + ", ".join(missing))

    max_rows = max(len(pl), len(barang))
    differences = []

    for i in range(max_rows):
        excel_row = i + 2  # asumsi header ada di baris Excel pertama

        def get(df, col):
            return df.iloc[i][col] if i < len(df) else None

        checks = [
            ("MATERIAL CODE / KODE BARANG", get(pl, pl_material), get(barang, barang_kode), "text"),
            ("ITEM NAME / URAIAN", get(pl, pl_item), get(barang, barang_uraian), "text"),
            ("QTY / JUMLAH SATUAN", get(pl, pl_qty), get(barang, barang_qty), "number"),
            ("NETTO / N/W", get(pl, pl_netto), get(barang, barang_netto), "number"),
            ("BRUTO / G/W", get(pl, pl_bruto), get(barang, barang_bruto), "number"),
        ]

        for field, pl_value, barang_value, _ in checks:
            if not values_equal(pl_value, barang_value):
                differences.append({
                    "BARIS EXCEL": excel_row,
                    "FIELD": field,
                    "PL": "" if pd.isna(pl_value) else pl_value,
                    "BARANG": "" if pd.isna(barang_value) else barang_value,
                })

    return differences, len(pl), len(barang)

st.sidebar.header("Upload File")
pl_file = st.sidebar.file_uploader("File PL", type=["xlsx", "xls"])
barang_file = st.sidebar.file_uploader("File BARANG", type=["xlsx", "xls"])

if pl_file and barang_file:
    pl_sheets = read_excel(pl_file)
    barang_sheets = read_excel(barang_file)

    pl_sheet = st.sidebar.selectbox("Sheet PL", list(pl_sheets.keys()), index=0)
    barang_sheet = st.sidebar.selectbox("Sheet BARANG", list(barang_sheets.keys()), index=0)

    if st.sidebar.button("🔍 Bandingkan", use_container_width=True):
        try:
            differences, pl_count, barang_count = compare_files(
                pl_file, barang_file, pl_sheet, barang_sheet
            )

            if not differences:
                # Sesuai permintaan: jika cocok, tidak ada notifikasi apa pun.
                st.session_state["comparison_done"] = True
                st.session_state["differences"] = []
                st.session_state["result_file"] = None
                st.rerun()

            result_df = pd.DataFrame(differences)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                result_df.to_excel(writer, index=False, sheet_name="PERBEDAAN")
            output.seek(0)

            st.session_state["comparison_done"] = True
            st.session_state["differences"] = differences
            st.session_state["result_file"] = output.getvalue()

        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

if st.session_state.get("comparison_done"):
    differences = st.session_state.get("differences", [])

    if differences:
        st.subheader("Perbedaan Ditemukan")
        st.dataframe(pd.DataFrame(differences), use_container_width=True, hide_index=True)

        result_file = st.session_state.get("result_file")
        if result_file:
            st.download_button(
                "⬇️ Download Hasil Perbandingan",
                data=result_file,
                file_name="hasil_perbandingan_PL_vs_BARANG.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
