import streamlit as st
import gspread
import pandas as pd
from datetime import date
from google.oauth2.service_account import Credentials

# -----------------------------------------------------------------
# KONFIGURASI HALAMAN & UI CUSTOM (MOBILE FRIENDLY & MODERN)
# -----------------------------------------------------------------
st.set_page_config(page_title="AlphaStock Journal", page_icon="📈", layout="wide")

# Custom CSS: Tema "Midnight Neon"
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #1a1a2e, #16213e, #0f3460);
        color: #E2E8F0;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #00E5FF !important;
        font-weight: 700 !important;
    }
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
    .stButton>button {
        background: linear-gradient(90deg, #00E5FF 0%, #0072FF 100%);
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: bold;
        width: 100%;
    }
    .stButton>button:hover {
        opacity: 0.8;
    }
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

@st.cache_data(ttl=15) # Cache 15 detik agar data GFinance lebih sering ter-refresh
def load_data(_client):
    try:
        spreadsheet = _client.open("Trade Journal") # Pastikan nama file GSheet benar
        worksheet = spreadsheet.worksheet("IDX")
        
        data = worksheet.get_all_values()
        if len(data) <= 1:
            return worksheet, pd.DataFrame(columns=COLUMNS)
            
        df = pd.DataFrame(data[1:], columns=COLUMNS)
        
        # --- FUNGSI CLEANING PINTAR ---
        # Menghapus Rp, koma, spasi, dan %. Jika ada #N/A, jadikan 0 agar tidak error.
        def clean_number(x):
            if isinstance(x, str):
                x = x.replace('Rp', '').replace(',', '').replace(' ', '').replace('%', '').strip()
                if x == '#N/A' or x == '' or x == '#ERROR!':
                    return 0.0
            try:
                return float(x)
            except:
                return 0.0

        # Terapkan cleaning ke kolom angka dan persentase
        numeric_cols = [
            "Price (Buy)", "Value (Buy)", "Current Price", "Custom Price", 
            "P&L", "P&L (Custom)", "Change %", "Change % (Custom)"
        ]
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].apply(clean_number)
                
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
tab_dash, tab_add, tab_update, tab_del = st.tabs(["📊 Dashboard", "➕ Entri Baru", "✏️ Update", "🗑️ Hapus"])

# ==========================================
# 1. TAB DASHBOARD (READ)
# ==========================================
with tab_dash:
    st.header("Overview Portfolio")
    
    if st.button("🔄 Refresh Data Real-Time", key="refresh_dash"):
        st.cache_data.clear()
        st.rerun()
        
    if not df.empty:
        # Filter posisi yang masih Open/Floating
        df_open = df[df['Possition'].str.contains('Open|Floating', case=False, na=False)]
        
        # Metrik Dashboard
        total_investasi = df_open['Value (Buy)'].sum() if 'Value (Buy)' in df_open else 0
        total_pnl = df_open['P&L'].sum() if 'P&L' in df_open else 0
        total_pnl_custom = df_open['P&L (Custom)'].sum() if 'P&L (Custom)' in df_open else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Value Aktif", f"Rp {total_investasi:,.0f}")
        col2.metric("Real-Time P&L", f"Rp {total_pnl:,.0f}")
        col3.metric("Custom P&L (Skenario)", f"Rp {total_pnl_custom:,.0f}")
        
        st.divider()
        st.markdown("**Semua Transaksi**")
        
        # Menampilkan Dataframe dengan format kolom yang cantik
        st.dataframe(
            df, 
            use_container_width=True,
            column_config={
                "Price (Buy)": st.column_config.NumberColumn(format="Rp %d"),
                "Value (Buy)": st.column_config.NumberColumn(format="Rp %d"),
                "Current Price": st.column_config.NumberColumn(format="Rp %d"),
                "Custom Price": st.column_config.NumberColumn(format="Rp %d"),
                "P&L": st.column_config.NumberColumn(format="Rp %d"),
                "P&L (Custom)": st.column_config.NumberColumn(format="Rp %d"),
                "Change %": st.column_config.NumberColumn(format="%.2f %%"),
                "Change % (Custom)": st.column_config.NumberColumn(format="%.2f %%"),
            }
        )
    else:
        st.info("Jurnal saham masih kosong. Tambahkan trade pertama Bapak di Tab ➕ Entri Baru.")

# ==========================================
# 2. TAB ENTRI BARU (CREATE)
# ==========================================
with tab_add:
    st.header("Tambah Pembelian Saham")
    
    with st.form("form_add_trade", clear_on_submit=True):
        col_in1, col_in2 = st.columns(2)
        
        with col_in1:
            input_date = st.date_input("Tanggal Beli", date.today())
            input_code = st.text_input("Kode Saham*", help="Contoh: BBCA").upper()
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
                    new_row = [
                        input_date.strftime("%Y-%m-%d"), 
                        input_code,                      
                        input_lot,                       
                        input_price,                     
                        "", # Value (Buy)
                        "", # Current Date
                        "", # Current Price
                        "", # Custom Date
                        "", # Custom Price
                        input_pos,                       
                        "", # Change %
                        "", # P&L
                        "", # Change % (Custom)
                        ""  # P&L (Custom)
                    ]
                    worksheet.append_row(new_row, value_input_option='USER_ENTERED')
                    st.cache_data.clear()
                    st.success(f"✅ Saham {input_code} berhasil ditambahkan!")
                    st.rerun()

# ==========================================
# 3. TAB UPDATE SKENARIO & POSISI (UPDATE)
# ==========================================
with tab_update:
    st.header("Update Posisi & Skenario")
    
    if not df.empty:
        df['Display_Str'] = df.index.astype(str) + " - " + df['Stock Code'] + " | " + df['Possition']
        selected_update = st.selectbox("Pilih Saham yang diupdate:", df['Display_Str'].tolist())
        
        if selected_update:
            idx = int(selected_update.split(" - ")[0])
            row_data = df.iloc[idx]
            gsheet_row = idx + 2 
            
            with st.form("form_update"):
                st.info(f"Mengedit: **{row_data['Stock Code']}**")
                
                col_up1, col_up2 = st.columns(2)
                with col_up1:
                    curr_pos = row_data.get('Possition', 'Open/Floating')
                    pos_index = 0 if 'Open' in str(curr_pos) else 1
                    update_pos = st.selectbox("Update Status", ["Open/Floating", "Closed"], index=pos_index)
                
                with col_up2:
                    update_custom_date = st.date_input("Custom Date (Skenario)", date.today())
                    
                if st.form_submit_button("Update Data"):
                    with st.spinner("Memperbarui GSheets..."):
                        updates = [
                            {'range': f'H{gsheet_row}', 'values': [[update_custom_date.strftime("%Y-%m-%d")]]},
                            {'range': f'J{gsheet_row}', 'values': [[update_pos]]}
                        ]
                        worksheet.batch_update(updates, value_input_option='USER_ENTERED')
                        st.cache_data.clear()
                        st.success("✅ Data berhasil diperbarui!")
                        st.rerun()

# ==========================================
# 4. TAB HAPUS (DELETE)
# ==========================================
with tab_del:
    st.header("Hapus Transaksi")
    if not df.empty:
        df['Display_Del'] = df.index.astype(str) + " - " + df['Stock Code']
        selected_delete = st.selectbox("Pilih transaksi yang ingin dihapus:", df['Display_Del'].tolist())
        
        if selected_delete:
            idx_del = int(selected_delete.split(" - ")[0])
            gsheet_row_del = idx_del + 2
            
            st.error(f"⚠️ Ini akan menghapus baris ke-{gsheet_row_del} di GSheets!")
            if st.button("🗑️ Konfirmasi Hapus Data"):
                with st.spinner("Menghapus baris..."):
                    worksheet.delete_rows(gsheet_row_del)
                    st.cache_data.clear()
                    st.success("✅ Transaksi dihapus!")
                    st.rerun()
