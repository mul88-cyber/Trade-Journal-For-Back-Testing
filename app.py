import streamlit as st
import gspread
import pandas as pd
import plotly.graph_objects as go
from datetime import date, datetime
import numpy as np
from google.oauth2.service_account import Credentials

# =========================================================================
# 🎨 THEME CONFIGURATION
# =========================================================================
if 'theme' not in st.session_state:
    st.session_state.theme = '🌙 Dark Korporat'

theme_options = {
    "🌙 Dark Korporat": {
        "bg": "linear-gradient(135deg, #2C3E50 0%, #34495E 100%)",
        "card_bg": "rgba(52, 73, 94, 0.3)",
        "accent": "#3498DB",
        "text": "#ECF0F1",
        "text_secondary": "#BDC3C7",
        "positive": "#2ECC71",
        "negative": "#E74C3C",
        "header_bg": "rgba(44, 62, 80, 0.7)"
    },
    "☀️ Light Professional": {
        "bg": "linear-gradient(135deg, #F5F7FA 0%, #E6ECF5 100%)",
        "card_bg": "rgba(255, 255, 255, 0.7)",
        "accent": "#3498DB",
        "text": "#2C3E50",
        "text_secondary": "#7F8C8D",
        "positive": "#27AE60",
        "negative": "#E74C3C",
        "header_bg": "rgba(255, 255, 255, 0.8)"
    }
}

def change_theme(theme_name):
    st.session_state.theme = theme_name
    st.rerun()

with st.sidebar:
    st.markdown("## 🎨 CUSTOM THEME")
    selected = st.selectbox("Pilih Theme", list(theme_options.keys()), 
                            index=list(theme_options.keys()).index(st.session_state.theme))
    if selected != st.session_state.theme:
        change_theme(selected)

theme = theme_options[st.session_state.theme]

st.set_page_config(page_title="AlphaStock Journal", page_icon="📈", layout="wide")

# =========================================================================
# 🔌 GOOGLE SHEETS CONNECTION (FIXED)
# =========================================================================
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
COLUMNS = ["Buy Date", "Stock Code", "Qty Lot", "Price (Buy)", "Value (Buy)", 
           "Current Date", "Current Price", "Custom Date", "Custom Price", 
           "Possition", "Change %", "P&L", "Change % (Custom)", "P&L (Custom)"]

@st.cache_resource(ttl=3600)
def get_gs_client():
    try:
        # Konversi secrets ke dict murni untuk menghindari error google-auth
        creds_info = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"❌ Koneksi Gagal: {e}")
        return None

def get_worksheet(client):
    if client:
        return client.open("Trade Journal").worksheet("IDX")
    return None

@st.cache_data(ttl=60)
def load_data_df(_client):
    try:
        ws = _client.open("Trade Journal").worksheet("IDX")
        data = ws.get_all_values()
        if len(data) <= 1:
            return pd.DataFrame(columns=COLUMNS)
        
        df = pd.DataFrame(data[1:], columns=COLUMNS)
        df = df[df['Stock Code'].str.strip() != '']
        
        # Cleaning Numeric
        numeric_cols = ["Price (Buy)", "Value (Buy)", "Current Price", "Custom Price", "P&L", "Qty Lot", "Change %"]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col].replace('[Rp,%\s]', '', regex=True), errors='coerce').fillna(0)
        
        # Cleaning Dates
        for col in ["Buy Date", "Custom Date"]:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            
        return df
    except Exception as e:
        st.error(f"❌ Gagal Load Data: {e}")
        return pd.DataFrame(columns=COLUMNS)

# Inisialisasi Data
client = get_gs_client()
df = load_data_df(client)
worksheet = get_worksheet(client)

# =========================================================================
# 🛠️ HELPER FUNCTIONS
# =========================================================================
def format_rupiah(angka):
    return f"Rp {float(angka):,.0f}".replace(',', '.')

# =========================================================================
# 📊 UI COMPONENTS (CSS)
# =========================================================================
st.markdown(f"""
    <style>
    .stApp {{ background: {theme['bg']}; color: {theme['text']}; }}
    div[data-testid="metric-container"] {{
        background: {theme['card_bg']}; border-radius: 15px; padding: 15px;
        border: 1px solid rgba(255,255,255,0.1);
    }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
    .stTabs [data-baseweb="tab"] {{
        background: {theme['card_bg']}; border-radius: 20px; color: white; padding: 10px 20px;
    }}
    .stTabs [aria-selected="true"] {{ background: {theme['accent']} !important; }}
    </style>
""", unsafe_allow_html=True)

st.title("📈 AlphaStock Trade Journal")

# =========================================================================
# 📑 TABS LOGIC
# =========================================================================
tabs = st.tabs(["📊 DASHBOARD", "➕ ENTRY", "✏️ UPDATE", "📈 ANALYTICS", "🗑️ DELETE"])

# --- TAB 0: DASHBOARD ---
with tabs[0]:
    if not df.empty:
        df_open = df[df['Possition'].str.contains('Open|Floating', case=False, na=False)]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("TOTAL PORTFOLIO", format_rupiah(df_open['Value (Buy)'].sum()))
        m2.metric("UNREALIZED P&L", format_rupiah(df_open['P&L'].sum()))
        m3.metric("WIN RATE", f"{(len(df[df['P&L']>0])/len(df)*100 if len(df)>0 else 0):.1f}%")
        m4.metric("ACTIVE POS", f"{len(df_open)} Stocks")
        
        st.subheader("📋 Porto Aktif")
        st.dataframe(df_open[['Buy Date', 'Stock Code', 'Qty Lot', 'Price (Buy)', 'P&L', 'Possition']], use_container_width=True)
    else:
        st.info("Data kosong. Silahkan ke Tab Entry.")

# --- TAB 1: ENTRY ---
with tabs[1]:
    st.subheader("➕ Tambah Transaksi")
    with st.form("form_entry", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        f_date = c1.date_input("Tanggal Beli", date.today())
        f_code = c2.text_input("Kode Saham (Contoh: BBCA)").upper()
        f_lot = c3.number_input("Jumlah Lot", min_value=1, step=1)
        f_price = c4.number_input("Harga Beli", min_value=1, step=1)
        submit = st.form_submit_button("Simpan ke Cloud")
        
        if submit and f_code:
            new_data = [f_date.strftime("%Y-%m-%d"), f_code, f_lot, f_price, "", "", "", "", "", "Open/Floating", "", "", "", ""]
            worksheet.append_row(new_data, value_input_option='USER_ENTERED')
            st.cache_data.clear()
            st.success("Berhasil disimpan!")
            st.rerun()

# --- TAB 2: UPDATE ---
with tabs[2]:
    st.subheader("✏️ Update Status/Scenario")
    if not df.empty:
        stock_list = df['Stock Code'].tolist()
        choice = st.selectbox("Pilih Saham", stock_list)
        idx = stock_list.index(choice)
        
        col_up1, col_up2 = st.columns(2)
        new_pos = col_up1.selectbox("Status", ["Open/Floating", "Closed"], index=0 if "Open" in df.iloc[idx]['Possition'] else 1)
        new_cust_date = col_up2.date_input("Custom Date", date.today())
        
        if st.button("Update Sekarang"):
            row_idx = idx + 2
            worksheet.update(f'J{row_idx}', [[new_pos]])
            worksheet.update(f'H{row_idx}', [[new_cust_date.strftime("%Y-%m-%d")]])
            st.cache_data.clear()
            st.success("Update Berhasil!")
            st.rerun()

# --- TAB 3: ANALYTICS ---
with tabs[3]:
    if not df.empty:
        fig = go.Figure(go.Bar(x=df['Stock Code'], y=df['P&L'], marker_color=theme['accent']))
        fig.update_layout(title="P&L per Saham", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 4: DELETE ---
with tabs[4]:
    if not df.empty:
        del_choice = st.selectbox("Hapus Transaksi", df['Stock Code'].tolist(), key="del")
        if st.button("🔥 HAPUS PERMANEN"):
            idx_to_del = df[df['Stock Code'] == del_choice].index[0] + 2
            worksheet.delete_rows(int(idx_to_del))
            st.cache_data.clear()
            st.warning("Data Dihapus!")
            st.rerun()

st.divider()
st.caption(f"Last Sync: {datetime.now().strftime('%H:%M:%S')} | AlphaStock Engine v2.1")
