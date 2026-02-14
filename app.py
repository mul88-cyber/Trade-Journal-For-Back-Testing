import streamlit as st
import gspread
import pandas as pd
import plotly.graph_objects as go
from datetime import date, datetime
import numpy as np
from google.oauth2.service_account import Credentials
import json

# =========================================================================
# MULTI-THEME SELECTOR (FIXED)
# =========================================================================

# Inisialisasi theme di session state
if 'theme' not in st.session_state:
    st.session_state.theme = '🌙 Dark Korporat'

# Fungsi ganti theme
def change_theme(theme_name):
    st.session_state.theme = theme_name
    st.rerun()

# Sidebar untuk pilih theme
with st.sidebar:
    st.markdown("## 🎨 CUSTOM THEME")
    
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
        "🌿 Green Forest": {
            "bg": "linear-gradient(135deg, #1B4D3E 0%, #2E7D5E 100%)",
            "card_bg": "rgba(46, 125, 94, 0.3)",
            "accent": "#FFC107",
            "text": "#F5F5F5",
            "text_secondary": "#CCCCCC",
            "positive": "#81C784",
            "negative": "#E57373",
            "header_bg": "rgba(27, 77, 62, 0.7)"
        },
        "💜 Royal Purple": {
            "bg": "linear-gradient(135deg, #2A1B3D 0%, #44318D 100%)",
            "card_bg": "rgba(68, 49, 141, 0.3)",
            "accent": "#FFB347",
            "text": "#F5F5F5",
            "text_secondary": "#D1C4E9",
            "positive": "#81C784",
            "negative": "#E57373",
            "header_bg": "rgba(42, 27, 61, 0.7)"
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
        },
        "🌅 Sunset Orange": {
            "bg": "linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%)",
            "card_bg": "rgba(255, 255, 255, 0.1)",
            "accent": "#FFFFFF",
            "text": "#FFFFFF",
            "text_secondary": "#F0F0F0",
            "positive": "#2ECC71",
            "negative": "#C0392B",
            "header_bg": "rgba(0, 0, 0, 0.2)"
        }
    }
    
    theme_keys = list(theme_options.keys())
    
    if st.session_state.theme in theme_keys:
        default_index = theme_keys.index(st.session_state.theme)
    else:
        default_index = 0
    
    selected = st.selectbox(
        "Pilih Theme",
        theme_keys,
        index=default_index,
        key="theme_selector"
    )
    
    if selected != st.session_state.theme:
        change_theme(selected)
    
    current = theme_options[st.session_state.theme]
    st.markdown(f"""
    <div style="
        background: {current['card_bg']};
        padding: 10px;
        border-radius: 10px;
        border-left: 4px solid {current['accent']};
        margin-top: 10px;
    ">
        <small>Active Theme:</small><br>
        <span style="color: {current['accent']};">{st.session_state.theme}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()

# Ambil theme yang aktif
theme = theme_options[st.session_state.theme]

# -----------------------------------------------------------------
# KONFIGURASI HALAMAN
# -----------------------------------------------------------------
st.set_page_config(
    page_title="AlphaStock Trade Journal", 
    page_icon="📈", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------
# CSS DINAMIS
# -----------------------------------------------------------------
st.markdown(f"""
    <style>
    .stApp {{
        background: {theme['bg']};
    }}
    
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 1400px !important;
        margin: 0 auto !important;
    }}
    
    .premium-header {{
        background: {theme['header_bg']};
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 30px;
        padding: 0.8rem 2rem;
        margin-bottom: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }}
    
    .header-title {{
        font-size: 1.8rem;
        font-weight: 700;
        color: {theme['text']};
    }}
    
    .header-title span {{
        color: {theme['accent']};
        font-weight: 300;
    }}
    
    .header-date {{
        color: {theme['text_secondary']};
        font-size: 0.9rem;
        background: rgba(255,255,255,0.03);
        padding: 0.5rem 1rem;
        border-radius: 20px;
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        background: {theme['card_bg']};
        backdrop-filter: blur(10px);
        padding: 4px;
        border-radius: 40px;
        border: 1px solid rgba(255,255,255,0.03);
        margin-bottom: 1.5rem;
        flex-wrap: nowrap;
        overflow-x: auto;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border-radius: 30px;
        padding: 0.5rem 1.2rem !important;
        color: {theme['text_secondary']};
        font-weight: 500;
        font-size: 0.9rem !important;
        transition: all 0.3s ease;
        white-space: nowrap;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: {theme['accent']} !important;
        color: white !important;
        box-shadow: 0 4px 10px {theme['accent']}80;
    }}
    
    div[data-testid="metric-container"] {{
        background: {theme['card_bg']} !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 16px !important;
        padding: 1rem !important;
        backdrop-filter: blur(8px);
    }}
    
    div[data-testid="metric-container"]:hover {{
        border-color: {theme['accent']} !important;
    }}
    
    div[data-testid="metric-container"] label {{
        color: {theme['text_secondary']} !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
    }}
    
    div[data-testid="metric-container"] div {{
        color: {theme['text']} !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
    }}
    
    .stDataFrame {{
        background: rgba(0,0,0,0.1);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.03);
        border-radius: 16px;
        overflow: hidden;
    }}
    
    .stDataFrame th {{
        background: {theme['card_bg']} !important;
        color: {theme['text']} !important;
        border-bottom: 2px solid {theme['accent']} !important;
    }}
    
    .stDataFrame td {{
        background: rgba(0,0,0,0.1) !important;
        color: {theme['text_secondary']} !important;
        border-bottom: 1px solid rgba(255,255,255,0.02) !important;
    }}
    
    .stDataFrame tr:hover td {{
        background: {theme['card_bg']} !important;
    }}
    
    .stButton>button {{
        background: {theme['accent']};
        color: white;
        border: none;
        border-radius: 30px !important;
        padding: 0.4rem 1.5rem !important;
        font-weight: 500;
        transition: all 0.3s ease;
    }}
    
    .stButton>button:hover {{
        opacity: 0.9;
        transform: translateY(-2px);
        box-shadow: 0 4px 10px {theme['accent']}80;
    }}
    
    div[data-baseweb="input"], div[data-baseweb="select"] {{
        background: {theme['card_bg']} !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 30px !important;
    }}
    
    div[data-baseweb="input"]:hover, div[data-baseweb="select"]:hover {{
        border-color: {theme['accent']} !important;
    }}
    
    input, select {{
        color: {theme['text']} !important;
    }}
    
    .stTextInput label, .stSelectbox label, .stDateInput label {{
        color: {theme['text_secondary']} !important;
    }}
    
    hr {{
        background: linear-gradient(90deg, transparent, {theme['accent']}, transparent) !important;
        height: 1px !important;
        border: none !important;
        margin: 1.5rem 0 !important;
        opacity: 0.3;
    }}
    
    ::-webkit-scrollbar {{
        width: 6px;
        height: 6px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {theme['card_bg']};
        border-radius: 10px;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {theme['accent']};
        border-radius: 10px;
    }}
    
    @media (max-width: 768px) {{
        .premium-header {{
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
        }}
        
        div[data-testid="metric-container"] div {{
            font-size: 1.2rem !important;
        }}
        
        .stDataFrame table {{
            min-width: 800px !important; 
        }}
    }}
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------
# HEADER
# -----------------------------------------------------------------
st.markdown(f"""
    <div class="premium-header">
        <div class="header-title">📈 AlphaStock <span>| Trade Journal</span></div>
        <div class="header-date">
            <span>📅 {datetime.now().strftime('%d %B %Y')}</span>
            <span style="margin-left: 1rem;">⏰ {datetime.now().strftime('%H:%M')}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# =========================================================================
# FIXED: KONEKSI GOOGLE SHEETS DENGAN METODE ALTERNATIF
# =========================================================================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

COLUMNS = [
    "Buy Date", "Stock Code", "Qty Lot", "Price (Buy)", "Value (Buy)", 
    "Current Date", "Current Price", "Custom Date", "Custom Price", 
    "Possition", "Change %", "P&L", "Change % (Custom)", "P&L (Custom)"
]

@st.cache_resource(ttl=300)
def get_gsheet_client():
    try:
        # 1. Ambil rahasia dan paksa jadi dictionary murni
        creds_info = st.secrets["gcp_service_account"]
        if hasattr(creds_info, "to_dict"):
            creds_info = creds_info.to_dict()
        else:
            creds_info = dict(creds_info)

        # 2. Buat credentials
        creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
        
        # 3. Authorize client
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"🔴 Gagal koneksi ke Google Sheets: {str(e)}")
        return None
        
        # Ambil credentials dari secrets
        creds_dict = st.secrets["gcp_service_account"]
        
        # FIX: Gunakan metode otentikasi dengan service_account dari dict
        # Bukan service_account_from_dict yang bermasalah
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
        
        return client
    except Exception as e:
        st.error(f"🔴 Gagal koneksi ke Google Sheets: {str(e)}")
        st.info("Tips: Pastikan file service account JSON sudah benar dan spreadsheet sudah di-share ke email service account")
        return None

@st.cache_data(ttl=30)
def load_data(_client):
    try:
        if _client is None:
            return None, pd.DataFrame()
            
        spreadsheet = _client.open("Trade Journal")
        worksheet = spreadsheet.worksheet("IDX")
        
        data = worksheet.get_all_values()
        if len(data) <= 1:
            return worksheet, pd.DataFrame(columns=COLUMNS)
            
        df = pd.DataFrame(data[1:], columns=COLUMNS)
        
        # Filter baris kosong
        df = df[df['Stock Code'].astype(str).str.strip() != '']
        
        # Fungsi cleaning
        def clean_number(x):
            if pd.isna(x) or x == '':
                return 0.0
            if isinstance(x, str):
                x = x.replace('Rp', '').replace(',', '').replace('%', '').strip()
                if x in ['#N/A', '#ERROR!', 'No Data', '-']:
                    return 0.0
            try:
                return float(x)
            except:
                return 0.0

        # Convert numeric columns
        numeric_cols = ["Price (Buy)", "Value (Buy)", "Current Price", "Custom Price", 
                       "P&L", "P&L (Custom)", "Change %", "Change % (Custom)", "Qty Lot"]
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].apply(clean_number)
        
        # Convert date columns
        date_cols = ["Buy Date", "Current Date", "Custom Date"]
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return worksheet, df
    except Exception as e:
        st.error(f"🔴 Gagal memuat data: {str(e)}")
        return None, pd.DataFrame()

# Initialize dengan try-except
try:
    client = get_gsheet_client()
    if client:
        worksheet, df = load_data(client)
    else:
        st.stop()
except Exception as e:
    st.error(f"❌ Fatal Error: {str(e)}")
    st.stop()

# Format function untuk separator ribuan
def format_rupiah(angka):
    if pd.isna(angka) or angka == 0:
        return "Rp 0"
    try:
        return f"Rp {float(angka):,.0f}".replace(',', '.')
    except:
        return "Rp 0"

# =========================================================================
# TABS
# =========================================================================
tabs = st.tabs(["📊 DASHBOARD", "➕ ENTRY", "✏️ UPDATE", "📈 ANALYTICS", "🗑️ DELETE"])

# ==========================================
# DASHBOARD
# ==========================================
with tabs[0]:
    if not df.empty:
        df_open = df[df['Possition'].str.contains('Open|Floating', case=False, na=False)]
        
        cols = st.columns(4)
        with cols[0]:
            total_val = df_open['Value (Buy)'].sum() if not df_open.empty else 0
            st.metric("💰 TOTAL PORTFOLIO", format_rupiah(total_val))
        with cols[1]:
            pnl = df_open['P&L'].sum() if not df_open.empty else 0
            pnl_pct = (pnl/total_val*100) if total_val > 0 else 0
            st.metric("📈 UNREALIZED P&L", format_rupiah(pnl), delta=f"{pnl_pct:.1f}%")
        with cols[2]:
            win_count = (df_open['P&L'] > 0).sum() if not df_open.empty else 0
            total_count = len(df_open)
            win_rate = (win_count/total_count*100) if total_count > 0 else 0
            st.metric("🎯 WIN RATE", f"{win_rate:.1f}%")
        with cols[3]:
            st.metric("📊 ACTIVE", f"{len(df_open)} positions")
        
        st.divider()
        
        st.subheader("📋 TRANSACTION HISTORY")
        
        display_cols = ['Buy Date', 'Stock Code', 'Qty Lot', 'Price (Buy)', 'Value (Buy)', 
                        'Possition', 'Current Price', 'Change %', 'P&L']
        df_display = df[display_cols].copy()
        
        df_display['Buy Date'] = df_display['Buy Date'].apply(lambda x: x.strftime('%d/%m/%y') if pd.notna(x) else '-')
        df_display['Price (Buy)'] = df_display['Price (Buy)'].apply(lambda x: f"Rp {x:,.0f}".replace(',', '.'))
        df_display['Value (Buy)'] = df_display['Value (Buy)'].apply(lambda x: f"Rp {x:,.0f}".replace(',', '.'))
        df_display['Current Price'] = df_display['Current Price'].apply(lambda x: f"Rp {x:,.0f}".replace(',', '.'))
        df_display['P&L'] = df_display['P&L'].apply(lambda x: f"Rp {x:,.0f}".replace(',', '.'))
        df_display['Change %'] = df_display['Change %'].apply(lambda x: f"{x:.1f}%")
        
        df_display = df_display.rename(columns={
            "Buy Date": "📅 DATE",
            "Stock Code": "📊 STOCK",
            "Qty Lot": "🔢 LOT",
            "Price (Buy)": "💰 BUY PRICE",
            "Value (Buy)": "💵 VALUE",
            "Possition": "📍 POS",
            "Current Price": "💹 CURRENT",
            "Change %": "📈 CHANGE",
            "P&L": "💲 P&L"
        })

        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            total_pnl = df['P&L'].sum()
            st.info(f"💰 Total Realized P&L: {format_rupiah(total_pnl)}")
        with col2:
            win_trades = (df['P&L'] > 0).sum()
            st.info(f"✅ Winning Trades: **{win_trades}**")
        with col3:
            loss_trades = (df['P&L'] < 0).sum()
            st.info(f"❌ Losing Trades: **{loss_trades}**")
            
    else:
        st.info("✨ Belum ada transaksi. Mulai dengan tab ENTRY")

# ==========================================
# ENTRY - CREATE
# ==========================================
with tabs[1]:
    st.subheader("➕ ADD NEW TRANSACTION")
    
    with st.form("entry_form", clear_on_submit=True):
        cols = st.columns([1.2, 1, 0.8, 1.2, 1])
        
        with cols[0]:
            buy_date = st.date_input("📅 BUY DATE", date.today())
        with cols[1]:
            stock_code = st.text_input("📊 STOCK CODE", "", placeholder="BBCA").upper()
        with cols[2]:
            qty_lot = st.number_input("🔢 LOT", 1, step=1)
        with cols[3]:
            price_buy = st.number_input("💰 BUY PRICE", 1, step=10)
        with cols[4]:
            position = st.selectbox("📍 POSITION", ["Open/Floating", "Closed"])
        
        submitted = st.form_submit_button("➕ ADD TRANSACTION", use_container_width=True)
        
        if submitted:
            if not stock_code:
                st.error("❌ Stock code wajib diisi!")
            else:
                try:
                    new_row = [
                        buy_date.strftime("%Y-%m-%d"),
                        stock_code,
                        qty_lot,
                        price_buy,
                        "", "", "", "", "",
                        position,
                        "", "", "", ""
                    ]
                    
                    with st.spinner("Menyimpan ke Google Sheets..."):
                        # FIXED: append_row dengan format yang benar
                        worksheet.append_row(new_row, value_input_option='USER_ENTERED')
                        
                        st.cache_data.clear()
                        st.success(f"✅ {stock_code} berhasil ditambahkan!")
                        st.balloons()
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# ==========================================
# UPDATE
# ==========================================
with tabs[2]:
    st.subheader("✏️ UPDATE TRANSACTION")
    
    if not df.empty:
        options = [
            f"{row['Stock Code']} - {row['Buy Date'].strftime('%d/%m/%y') if pd.notna(row['Buy Date']) else '-'} - {format_rupiah(row['Price (Buy)'])}" 
            for _, row in df.iterrows()
        ]
        
        if options:
            selected = st.selectbox("Pilih transaksi:", options)
            
            if selected:
                idx = options.index(selected)
                row = df.iloc[idx]
                gsheet_row = idx + 2
                
                st.info(f"**Mengedit:** {row['Stock Code']} - Beli: {format_rupiah(row['Price (Buy)'])}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    new_position = st.selectbox(
                        "📍 Update Position",
                        ["Open/Floating", "Closed"],
                        index=0 if 'Open' in str(row['Possition']) else 1
                    )
                
                with col2:
                    default_date = row['Custom Date'] if pd.notna(row['Custom Date']) else date.today()
                    custom_date = st.date_input("📅 Custom Date (Skenario)", default_date)
                
                if st.button("🔄 UPDATE", use_container_width=True):
                    try:
                        with st.spinner("Updating..."):
                            # FIXED: Menggunakan update dengan range yang tepat
                            worksheet.update(
                                f'J{gsheet_row}', 
                                [[new_position]], 
                                value_input_option='USER_ENTERED'
                            )
                            worksheet.update(
                                f'H{gsheet_row}', 
                                [[custom_date.strftime("%Y-%m-%d")]], 
                                value_input_option='USER_ENTERED'
                            )
                            
                            st.cache_data.clear()
                            st.success("✅ Data berhasil diupdate!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        else:
            st.info("Tidak ada transaksi untuk diupdate")
    else:
        st.info("Belum ada transaksi untuk diupdate")

# ==========================================
# ANALYTICS
# ==========================================
with tabs[3]:
    st.subheader("📈 ANALYTICS DASHBOARD")
    
    if not df.empty:
        df_open = df[df['Possition'].str.contains('Open', case=False, na=False)]
        
        if not df_open.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = go.Figure()
                colors = [theme['positive'] if x > 0 else theme['negative'] for x in df_open['P&L']]
                
                fig.add_trace(go.Bar(
                    x=df_open['Stock Code'],
                    y=df_open['P&L'],
                    marker_color=colors,
                    text=df_open['P&L'].apply(lambda x: f'Rp {x:,.0f}'),
                    textposition='outside',
                    textfont=dict(size=10, color=theme['text'])
                ))
                
                fig.update_layout(
                    title="📊 P&L per Saham",
                    template="plotly_dark",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=theme['text']),
                    height=300,
                    margin=dict(l=20, r=20, t=40, b=20),
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                wins = (df_open['P&L'] > 0).sum()
                losses = (df_open['P&L'] < 0).sum()
                
                if wins + losses > 0:
                    fig = go.Figure(data=[go.Pie(
                        labels=['WIN', 'LOSS'],
                        values=[wins, losses],
                        marker_colors=[theme['positive'], theme['negative']],
                        textinfo='label+percent',
                        textfont=dict(size=12, color=theme['text']),
                        hole=0.4
                    )])
                    
                    fig.update_layout(
                        title="🎯 Win/Loss Ratio",
                        template="plotly_dark",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color=theme['text']),
                        height=300,
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            st.subheader("📊 RISK METRICS")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                volatility = df_open['Change %'].std() if len(df_open) > 1 else 0
                st.metric("📉 Volatility", f"{volatility:.2f}%")
            with col2:
                avg_return = df_open['Change %'].mean()
                st.metric("📈 Avg Return", f"{avg_return:.2f}%")
            with col3:
                max_loss = df_open['P&L'].min()
                st.metric("🔻 Max Loss", format_rupiah(max_loss))
            with col4:
                max_gain = df_open['P&L'].max()
                st.metric("🔺 Max Gain", format_rupiah(max_gain))
        else:
            st.info("Tidak ada posisi open untuk analitik")
    else:
        st.info("Tambah transaksi untuk melihat analitik")

# ==========================================
# DELETE
# ==========================================
with tabs[4]:
    st.subheader("🗑️ DELETE TRANSACTION")
    
    if not df.empty:
        options = [
            f"{row['Stock Code']} - {row['Buy Date'].strftime('%d/%m/%y') if pd.notna(row['Buy Date']) else '-'} - {format_rupiah(row['Value (Buy)'])}" 
            for _, row in df.iterrows()
        ]
        
        if options:
            to_delete = st.selectbox("Pilih transaksi untuk dihapus:", options)
            
            if to_delete:
                idx = options.index(to_delete)
                row = df.iloc[idx]
                gsheet_row = idx + 2
                
                st.warning(f"⚠️ PERMANENT DELETE: **{row['Stock Code']}**")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ KONFIRMASI DELETE", use_container_width=True):
                        try:
                            with st.spinner("Menghapus..."):
                                # FIXED: delete_rows dengan parameter yang benar
                                worksheet.delete_rows(gsheet_row)
                                
                                st.cache_data.clear()
                                st.success("✅ Transaksi dihapus!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                with col2:
                    if st.button("BATAL", use_container_width=True):
                        st.rerun()
        else:
            st.info("Tidak ada transaksi untuk dihapus")
    else:
        st.info("Belum ada transaksi untuk dihapus")

# -----------------------------------------------------------------
# FOOTER
# -----------------------------------------------------------------
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"📊 Total Transaksi: {len(df) if not df.empty else 0}")
with col2:
    st.caption(f"📈 Total Saham: {df['Stock Code'].nunique() if not df.empty else 0}")
with col3:
    st.caption(f"⚡ Last Update: {datetime.now().strftime('%H:%M:%S')}")
