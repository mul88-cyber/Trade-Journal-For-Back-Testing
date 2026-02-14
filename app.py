import streamlit as st
import gspread
import pandas as pd
from datetime import date, datetime
import pytz
from google.oauth2.service_account import Credentials

# -----------------------------------------------------------------
# KONFIGURASI HALAMAN & UI CUSTOM (MOBILE FRIENDLY & MODERN)
# -----------------------------------------------------------------
st.set_page_config(page_title="AlphaStock Journal", page_icon="📈", layout="wide")

# Custom CSS: Tema "Midnight Neon" - Tajam, Elegan, dan Mobile-Ready
st.markdown("""
    <style>
    /* Background & Global Font Color */
    .stApp {
        background: radial-gradient(circle at top left, #1a1a2e, #16213e, #0f3460);
        color: #E2E8F0;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #00E5FF !important;
        font-weight: 700 !important;
    }
    /* Styling Tabs agar lebih modern di Mobile */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1A202C;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 16px;
        color: #A0AEC0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00E5FF;
        color: #1A202C !important;
        font-weight: bold;
    }
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #00E5FF 0%, #0072FF 100%);
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: bold;
        width: 100%; /* Full width for mobile */
    }
    .stButton>button:hover {
        opacity: 0.8;
        border: none;
    }
    /* Dataframes & inputs */
    [data-baseweb="input"], [data-baseweb="select"] {
        background-color: #1A202C !important;
        border-radius: 6px !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 AlphaStock Journal")
st.markdown("*Professional Stock Trading Tracker & What-If Analyzer*")

# -----------------------------------------------------------------
# KONEKSI KE GOOGLE SHEETS
# -----------------------------------------------------------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Urutan kolom WAJIB SAMA dengan di GSheet "IDX"
COLUMNS = [
    "Buy Date", "Stock Code", "Qty Lot", "Price (Buy)", "Value (Buy)", 
    "Current Date", "Current Price", "Custom Date", "Custom Price", 
    "Possition", "Change %", "P&L", "Change % (Custom)", "P&L (Custom)"
]

@st.cache_resource(ttl=300)
def get_gsheet_client():
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client

@st.cache_data(ttl=30) # Dipercepat jadi 30 detik untuk kenyamanan update
def load_data(_client):
    try:
        spreadsheet = _client.open("Trade Journal") # Ganti nama file ini jika berbeda
        worksheet = spreadsheet.worksheet("IDX")
        
        data = worksheet.get_all_values()
        if len(data) <= 1:
            return worksheet, pd.DataFrame(columns=COLUMNS)
            
        df = pd.DataFrame(data[1:], columns=COLUMNS)
        
        # Bersihkan format angka/uang (P&L, Harga, dll) agar bisa dibaca Pandas
        # Hapus 'Rp', koma, spasi, dan '%' lalu jadikan float
        cols_to_clean = ["Price (Buy)", "Value (Buy)", "Current Price", "Custom Price", "P&L", "P&L (Custom)"]
        for col in cols_to_clean:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(r'[Rp,%\s]', '', regex=True)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
        return worksheet, df
    except Exception as e:
        st.error(f"Gagal memuat data GSheet: {e}")
        return None, pd.DataFrame()

# INISIALISASI
client = get_gsheet_client()
if client:
    worksheet, df = load_data(client)
else:
    st.stop()

# -----------------------------------------------------------------
# TAB INTERFACE (CRUD)
# -----------------------------------------------------------------
tab_dash, tab_add, tab_update, tab_del = st.tabs(["📊 Dashboard", "➕ Entri Baru", "✏️ Update Skenario", "🗑️ Hapus"])

# ==========================================
# 1. TAB DASHBOARD (READ)
# ==========================================
with tab_dash:
    st.header("Overview Portfolio")
    
    if st.button("🔄 Refresh Data", key="refresh_dash"):
        st.cache_data.clear()
        st.rerun()
        
    if not df.empty:
        df_open = df[df['Possition'].str.contains('Open|Floating', case=False, na=False)]
        
        # Quick Metrik (Kalkulasi dari kolom P&L yang sudah di-clean jadi numeric)
        total_investasi = df_open['Value (Buy)'].sum() if 'Value (Buy)' in df_open else 0
        total_pnl = df_open['P&L'].sum() if 'P&L' in df_open else 0
        total_pnl_custom = df_open['P&L (Custom)'].sum() if 'P&L (Custom)' in df_open else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Value Aktif", f"Rp {total_investasi:,.0f}")
        col2.metric("Real-Time P&L", f"Rp {total_pnl:,.0f}", delta=f"Rp {total_pnl:,.0f}")
        col3.metric("Custom P&L (Skenario)", f"Rp {total_pnl_custom:,.0f}", delta=f"Rp {total_pnl_custom:,.0f}", delta_color="off")
        
        st.divider()
        st.markdown("**Semua Transaksi**")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Jurnal saham masih kosong. Tambahkan trade pertama Bapak di Tab ➕ Entri Baru.")

# ==========================================
# 2. TAB ENTRI BARU (CREATE)
# ==========================================
with tab_add:
    st.header("Tambah Pembelian Saham")
    st.markdown("Kolom kalkulasi otomatis akan diurus oleh Google Sheets.")
    
    with st.form("form_add_trade", clear_on_submit=True):
        col_in1, col_in2 = st.columns(2)
        
        with col_in1:
            input_date = st.date_input("Tanggal Beli", date.today())
            input_code = st.text_input("Kode Saham*", help="Contoh: BBCA, TLKM").upper()
            input_lot = st.number_input("Jumlah (Lot)*", min_value=1, step=1)
            
        with col_in2:
            input_price = st.number_input("Harga Beli (Rp)*", min_value=1, step=1)
            input_pos = st.selectbox("Posisi Awal*", ["Open/Floating", "Closed"])
            
        submit_add = st.form_submit_button("Simpan Trade")
        
        if submit_add:
            if not input_code:
                st.error("❌ Kode Saham tidak boleh kosong!")
            else:
                with st.spinner("Menyimpan ke Google Sheets..."):
                    # Mapping array ke kolom (14 Kolom)
                    new_row = [
                        input_date.strftime("%Y-%m-%d"), # 1. Buy Date
                        input_code,                      # 2. Stock Code
                        input_lot,                       # 3. Qty Lot
                        input_price,                     # 4. Price (Buy)
                        "",                              # 5. Value (Buy) -> Rumus Gsheet
                        "",                              # 6. Current Date -> Rumus Gsheet
                        "",                              # 7. Current Price -> Rumus Gsheet
                        "",                              # 8. Custom Date -> Kosong dlu
                        "",                              # 9. Custom Price -> Rumus
                        input_pos,                       # 10. Possition
                        "",                              # 11. Change % -> Rumus
                        "",                              # 12. P&L -> Rumus
                        "",                              # 13. Change % (Custom) -> Rumus
                        ""                               # 14. P&L (Custom) -> Rumus
                    ]
                    worksheet.append_row(new_row, value_input_option='USER_ENTERED')
                    st.cache_data.clear()
                    st.success(f"✅ Saham {input_code} berhasil ditambahkan!")
                    st.rerun()

# ==========================================
# 3. TAB UPDATE SKENARIO & POSISI (UPDATE)
# ==========================================
with tab_update:
    st.header("Update Posisi & Skenario What-If")
    st.markdown("Pilih transaksi untuk mengupdate status *Position* atau mengisi *Custom Date*.")
    
    if not df.empty:
        # Bikin helper dropdown
        # Peringatan: index pandas mulai 0, data asli GSheet row mulai 2 (karena header di row 1)
        df['Display_Str'] = df.index.astype(str) + " - " + df['Stock Code'] + " | " + df['Possition']
        
        selected_update = st.selectbox("Pilih Saham yang diupdate:", df['Display_Str'].tolist())
        
        if selected_update:
            idx = int(selected_update.split(" - ")[0])
            row_data = df.iloc[idx]
            gsheet_row = idx + 2 # +2 karena ada header dan index pandas mulai 0
            
            with st.form("form_update"):
                st.info(f"Mengedit: **{row_data['Stock Code']}** (Beli di Rp {row_data['Price (Buy)']:,})")
                
                col_up1, col_up2 = st.columns(2)
                with col_up1:
                    # Index dropdown menyesuaikan nilai saat ini
                    curr_pos = row_data.get('Possition', 'Open/Floating')
                    pos_index = 0 if 'Open' in str(curr_pos) else 1
                    update_pos = st.selectbox("Update Status Posisi", ["Open/Floating", "Closed"], index=pos_index)
                
                with col_up2:
                    update_custom_date = st.date_input("Custom Date (Skenario)", date.today())
                    
                submit_update = st.form_submit_button("Update Data")
                
                if submit_update:
                    with st.spinner("Memperbarui data di GSheets..."):
                        # Kita gunakan batch_update agar cepat!
                        # Custom Date = Kolom H (ke-8)
                        # Possition = Kolom J (ke-10)
                        updates = [
                            {'range': f'H{gsheet_row}', 'values': [[update_custom_date.strftime("%Y-%m-%d")]]},
                            {'range': f'J{gsheet_row}', 'values': [[update_pos]]}
                        ]
                        worksheet.batch_update(updates, value_input_option='USER_ENTERED')
                        st.cache_data.clear()
                        st.success("✅ Data berhasil diperbarui!")
                        st.rerun()
    else:
        st.warning("Data masih kosong.")

# ==========================================
# 4. TAB HAPUS (DELETE)
# ==========================================
with tab_del:
    st.header("Hapus Transaksi (Danger Zone)")
    if not df.empty:
        df['Display_Del'] = df.index.astype(str) + " - " + df['Stock Code'] + " | Beli: " + df['Buy Date'].astype(str)
        selected_delete = st.selectbox("Pilih transaksi yang ingin dihapus:", df['Display_Del'].tolist())
        
        if selected_delete:
            idx_del = int(selected_delete.split(" - ")[0])
            gsheet_row_del = idx_del + 2
            
            st.error(f"⚠️ Peringatan: Ini akan menghapus baris ke-{gsheet_row_del} di Google Sheets secara permanen!")
            if st.button("🗑️ Konfirmasi Hapus Data"):
                with st.spinner("Menghapus baris..."):
                    worksheet.delete_rows(gsheet_row_del)
                    st.cache_data.clear()
                    st.success("✅ Transaksi berhasil dihapus!")
                    st.rerun()
    else:
        st.info("Tidak ada data untuk dihapus.")
