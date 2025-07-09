import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd
import altair as alt

# ✅ Setup Google Sheets access via Streamlit secrets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
key_dict = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
client = gspread.authorize(creds)

# URL dan worksheet
sheet_url = "https://docs.google.com/spreadsheets/d/1gch3ROD7veg-FtBqgtRXtM93yd9tlLR4-oec8GNtZ_c/edit#gid=0"
sheet = client.open_by_url(sheet_url)
worksheet = sheet.worksheet("Data")

# Ambil data
data = worksheet.get_all_records()
df = pd.DataFrame(data)

st.set_page_config(page_title="Aplikasi Keuangan", layout="wide")
st.title("📒 Aplikasi Pencatatan Income & Outcome")

# Tabs utama
tab1, tab2 = st.tabs(["📥 Input & Riwayat", "📚 Semua Data Pengguna"])

with tab1:
    user_list = sorted(df['User'].dropna().unique().tolist()) if not df.empty else []
    user = st.sidebar.selectbox("👤 Pilih / Masukkan Nama Pengguna", options=user_list + ["➕ Tambah Baru"])

    if user == "➕ Tambah Baru":
        user = st.sidebar.text_input("Masukkan Nama Pengguna Baru")

    if not user:
        st.sidebar.warning("Silakan isi nama pengguna terlebih dahulu.")
        st.stop()

    user_df = df[df["User"] == user] if not df.empty else pd.DataFrame()

    existing_categories = user_df["Category"].dropna().unique().tolist() if not user_df.empty else []
    if not existing_categories:
        existing_categories = ['Gaji', 'Makanan', 'Transportasi']

    # Input transaksi
    st.sidebar.header("📥 Input Transaksi")
    date = st.sidebar.date_input("Tanggal", datetime.today())
    trans_type = st.sidebar.selectbox("Tipe", ["Income", "Outcome"])
    default_category = 'Gaji' if trans_type == "Income" and 'Gaji' in existing_categories else existing_categories[0]
    category = st.sidebar.selectbox("Pilih Kategori", existing_categories, index=existing_categories.index(default_category))
    add_new_category = st.sidebar.checkbox("➕ Tambah Kategori Baru")
    if add_new_category:
        new_category = st.sidebar.text_input("Kategori Baru")
        final_category = new_category.strip() if new_category.strip() else category
    else:
        final_category = category

    amount = st.sidebar.number_input("Jumlah (Rp)", min_value=0)
    notes = st.sidebar.text_input("Catatan")

    if st.sidebar.button("💾 Simpan"):
        if final_category:
            worksheet.append_row([user, str(date), trans_type, final_category, amount, notes])
            st.sidebar.success("Data berhasil disimpan!")
            st.rerun()
        else:
            st.sidebar.error("Kategori tidak boleh kosong.")

    # Fitur hapus transaksi
    st.sidebar.markdown("---")
    st.sidebar.header("🗑️ Hapus Transaksi")

    if not user_df.empty:
        user_df["Amount"] = pd.to_numeric(user_df["Amount"], errors="coerce")
        user_df["RowIndex"] = user_df.index + 2
        user_df["Label"] = user_df.apply(
            lambda row: f"{row['Date']} - {row['Type']} - {row['Category']} - Rp{row['Amount']}", axis=1
        )
        selected_label = st.sidebar.selectbox("Pilih Transaksi", user_df["Label"])
        selected_row = user_df[user_df["Label"] == selected_label]

        if st.sidebar.button("❌ Hapus Transaksi"):
            row_to_delete = selected_row["RowIndex"].values[0]
            worksheet.delete_rows(int(row_to_delete))
            st.sidebar.success("Transaksi berhasil dihapus!")
            st.rerun()
    else:
        st.sidebar.info("Belum ada data untuk dihapus.")

    st.subheader(f"📊 Riwayat Transaksi: {user}")
    if df.empty or user_df.empty:
        st.info("Belum ada transaksi untuk pengguna ini.")
        st.stop()

    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    user_df = df[df["User"] == user]

    st.markdown("### 🔍 Filter Data")
    months = user_df["Date"].dt.month_name().unique()
    years = user_df["Date"].dt.year.unique()
    selected_month = st.selectbox("Bulan", sorted(months))
    selected_year = st.selectbox("Tahun", sorted(years))

    filtered_df = user_df[
        (user_df["Date"].dt.month_name() == selected_month) &
        (user_df["Date"].dt.year == selected_year)
    ]

    st.dataframe(filtered_df, use_container_width=True)

    if not filtered_df.empty:
        filtered_df['Amount'] = pd.to_numeric(filtered_df['Amount'], errors='coerce')
        total_income = filtered_df[filtered_df['Type'] == 'Income']['Amount'].sum()
        total_outcome = filtered_df[filtered_df['Type'] == 'Outcome']['Amount'].sum()
        balance = total_income - total_outcome

        st.markdown(f"### 💰 Total Income: Rp {total_income:,.0f}")
        st.markdown(f"### 🧾 Total Outcome: Rp {total_outcome:,.0f}")
        st.markdown(f"### 📌 Balance: Rp {balance:,.0f}")

        st.subheader("📈 Visualisasi Data")
        col1, col2 = st.columns(2)

        with col1:
            outcome_by_cat = filtered_df[filtered_df['Type'] == 'Outcome'].groupby('Category')['Amount'].sum().reset_index()
            if not outcome_by_cat.empty:
                pie = alt.Chart(outcome_by_cat).mark_arc().encode(
                    theta="Amount",
                    color=alt.Color("Category", scale=alt.Scale(scheme='category20b')),
                    tooltip=["Category", "Amount"]
                ).properties(title="Distribusi Pengeluaran")
                st.altair_chart(pie, use_container_width=True)
            else:
                st.info("Tidak ada data pengeluaran.")

        with col2:
            summary = filtered_df.groupby(['Date', 'Type'])['Amount'].sum().reset_index()
            bar = alt.Chart(summary).mark_bar().encode(
                x="Date:T",
                y="Amount:Q",
                color=alt.Color("Type:N", scale=alt.Scale(range=['#00C49F', '#FF8042'])),
                tooltip=["Date", "Type", "Amount"]
            ).properties(title="Income vs Outcome Harian")
            st.altair_chart(bar, use_container_width=True)
    else:
        st.warning("Tidak ada data untuk bulan & tahun ini.")

with tab2:
    st.subheader("📚 Semua Data Pengguna")
    if df.empty:
        st.info("Belum ada data yang tersedia.")
        st.stop()

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

    user_summary = df.groupby(["User", "Type"])["Amount"].sum().reset_index()
    income_df = user_summary[user_summary["Type"] == "Income"]
    outcome_df = user_summary[user_summary["Type"] == "Outcome"]

    st.markdown("### 📊 Total Income dan Outcome per Pengguna")
    income_chart = alt.Chart(income_df).mark_bar().encode(
        x=alt.X("User:N", sort='-y'),
        y="Amount:Q",
        color=alt.Color("User:N", scale=alt.Scale(scheme='tableau10')),
        tooltip=["User", "Amount"]
    ).properties(title="Total Income per User")

    outcome_chart = alt.Chart(outcome_df).mark_bar().encode(
        x=alt.X("User:N", sort='-y'),
        y="Amount:Q",
        color=alt.Color("User:N", scale=alt.Scale(scheme='tableau20')),
        tooltip=["User", "Amount"]
    ).properties(title="Total Outcome per User")

    col1, col2 = st.columns(2)
    with col1:
        st.altair_chart(income_chart, use_container_width=True)
    with col2:
        st.altair_chart(outcome_chart, use_container_width=True)

    st.markdown("### 📈 Tren Income dan Outcome Bulanan")
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    trend_df = df.groupby(["Month", "Type"])["Amount"].sum().reset_index()

    line_chart = alt.Chart(trend_df).mark_line(point=True).encode(
        x="Month:T",
        y="Amount:Q",
        color=alt.Color("Type:N", scale=alt.Scale(scheme='set1')),
        tooltip=["Month", "Type", "Amount"]
    ).properties(title="Tren Bulanan Semua Pengguna")

    st.altair_chart(line_chart, use_container_width=True)

    st.markdown("### 🗃️ Tabel Lengkap Transaksi Semua Pengguna")
    st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)
