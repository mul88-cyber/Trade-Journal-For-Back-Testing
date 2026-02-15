import streamlit as st
import gspread
import pandas as pd
import plotly.graph_objects as go
from datetime import date, datetime
import numpy as np
from google.oauth2.service_account import Credentials
import time

# =========================================================================
# MULTI-THEME SELECTOR 
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
    
    # Quick Stats in Sidebar
    st.markdown("### 📌 Quick Stats")

# Ambil theme yang aktif
theme = theme_options[st.session_state.theme]

# -----------------------------------------------------------------
# KONFIGURASI HALAMAN
# -----------------------------------------------------------------
st.set_page_config(
    page_title="IDX Trade Journal", 
    page_icon="📈", 
    layout="wide",
    initial_sidebar_state="expanded"
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
    
    .stTextInput label, .stSelectbox label, .stDateInput label, .stNumberInput label {{
        color: {theme['text_secondary']} !important;
        font-size: 0.85rem !important;
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
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {{
        background: {theme['bg']};
    }}
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label {{
        color: {theme['text']} !important;
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
# HEADER WITH REFRESH BUTTON
# -----------------------------------------------------------------
col1, col2 = st.columns([5, 1])
with col1:
    st.markdown(f"""
        <div class="premium-header">
            <div class="header-title">📈 IDX Trade <span>| Backtesting Journal</span></div>
            <div class="header-date">
                <span>📅 {datetime.now().strftime('%d %B %Y')}</span>
                <span style="margin-left: 1rem;">⏰ {datetime.now().strftime('%H:%M')}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.write("")
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# =========================================================================
# KONEKSI GOOGLE SHEETS
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
        if "gcp_service_account" not in st.secrets:
            st.error("❌ Gagal: secrets 'gcp_service_account' tidak ditemukan!")
            return None
        
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"🔴 Gagal koneksi ke Google Sheets: {str(e)}")
        return None

def get_worksheet(_client):
    if _client:
        try:
            return _client.open_by_key(st.secrets["spreadsheet_id"]).sheet1
        except Exception as e:
            st.error(f"🔴 Gagal mengambil Worksheet: {str(e)}")
    return None

@st.cache_data(ttl=30)
def load_data(_client):
    try:
        if _client is None:
            return pd.DataFrame(columns=COLUMNS)
            
        spreadsheet = _client.open_by_key(st.secrets["spreadsheet_id"])
        ws = spreadsheet.sheet1
        
        data = ws.get_all_values()
        if len(data) <= 1:
            return pd.DataFrame(columns=COLUMNS)
            
        df = pd.DataFrame(data[1:], columns=COLUMNS)
        df = df[df['Stock Code'].astype(str).str.strip() != '']
        
        def clean_number(x):
            if pd.isna(x) or x == '':
                return 0.0
            if isinstance(x, str):
                x = x.replace('Rp', '').replace(',', '').replace('%', '').replace('.', '').strip()
                if x in ['#N/A', '#ERROR!', 'No Data', '-', '']:
                    return 0.0
            try:
                return float(x)
            except:
                return 0.0

        numeric_cols = ["Price (Buy)", "Value (Buy)", "Current Price", "Custom Price", 
                        "P&L", "P&L (Custom)", "Change %", "Change % (Custom)", "Qty Lot"]
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].apply(clean_number)
        
        date_cols = ["Buy Date", "Current Date", "Custom Date"]
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"🔴 Gagal memuat data: {str(e)}")
        return pd.DataFrame(columns=COLUMNS)

# Initialize
try:
    client = get_gsheet_client()
    df = load_data(client)
    worksheet = get_worksheet(client) 
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

# Update sidebar quick stats
with st.sidebar:
    if not df.empty:
        open_positions = len(df[df['Possition'].str.contains('Open|Floating', case=False, na=False)])
        closed_positions = len(df[~df['Possition'].str.contains('Open|Floating', case=False, na=False)])
        st.metric("🔓 Open Positions", open_positions)
        st.metric("🔒 Closed Positions", closed_positions)
        st.metric("📊 Total Trades", len(df))
    else:
        st.info("No trades yet")

# =========================================================================
# TABS
# =========================================================================
tabs = st.tabs(["📊 DASHBOARD", "➕ ADD TRADE", "✏️ UPDATE", "📈 ANALYTICS", "🗑️ DELETE", "📋 ALL TRADES"])

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
        
        # Charts side by side
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Top 10 P&L")
            if not df_open.empty:
                chart_df = df_open.nlargest(10, 'P&L') if len(df_open) > 10 else df_open
                colors = [theme['positive'] if x > 0 else theme['negative'] for x in chart_df['P&L']]
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=chart_df['Stock Code'],
                    y=chart_df['P&L'],
                    marker_color=colors,
                    text=chart_df['P&L'].apply(lambda x: format_rupiah(x)),
                    textposition='outside',
                    textfont=dict(size=10, color=theme['text'])
                ))
                
                fig.update_layout(
                    template="plotly_dark",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=theme['text']),
                    height=300,
                    margin=dict(l=20, r=20, t=10, b=20),
                    showlegend=False,
                    xaxis_title="",
                    yaxis_title=""
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🥧 Position Status")
            position_open = len(df[df['Possition'].str.contains('Open|Floating', case=False, na=False)])
            position_closed = len(df) - position_open
            
            if position_open + position_closed > 0:
                fig = go.Figure(data=[go.Pie(
                    labels=['OPEN', 'CLOSED'],
                    values=[position_open, position_closed],
                    marker_colors=[theme['accent'], theme['text_secondary']],
                    textinfo='label+percent',
                    textfont=dict(size=12, color=theme['text']),
                    hole=0.4
                )])
                
                fig.update_layout(
                    template="plotly_dark",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=theme['text']),
                    height=300,
                    margin=dict(l=20, r=20, t=10, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        st.subheader("📋 RECENT TRADES")
        
        display_cols = ['Buy Date', 'Stock Code', 'Qty Lot', 'Price (Buy)', 'Value (Buy)', 
                        'Possition', 'Current Price', 'Change %', 'P&L']
        df_display = df.head(10)[display_cols].copy()
        
        df_display['Buy Date'] = df_display['Buy Date'].apply(lambda x: x.strftime('%d/%m/%y') if pd.notna(x) else '-')
        df_display['Price (Buy)'] = df_display['Price (Buy)'].apply(format_rupiah)
        df_display['Value (Buy)'] = df_display['Value (Buy)'].apply(format_rupiah)
        df_display['Current Price'] = df_display['Current Price'].apply(format_rupiah)
        df_display['P&L'] = df_display['P&L'].apply(format_rupiah)
        df_display['Change %'] = df_display['Change %'].apply(lambda x: f"{x:.1f}%")
        
        df_display = df_display.rename(columns={
            "Buy Date": "📅 DATE",
            "Stock Code": "📊 STOCK",
            "Qty Lot": "🔢 LOT",
            "Price (Buy)": "💰 BUY",
            "Value (Buy)": "💵 VALUE",
            "Possition": "📍 POS",
            "Current Price": "💹 CURRENT",
            "Change %": "📈 %",
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
            st.info(f"💰 Total P&L: {format_rupiah(total_pnl)}")
        with col2:
            win_trades = (df['P&L'] > 0).sum()
            st.info(f"✅ Winning: **{win_trades}**")
        with col3:
            loss_trades = (df['P&L'] < 0).sum()
            st.info(f"❌ Losing: **{loss_trades}**")
            
    else:
        st.info("✨ Belum ada transaksi. Mulai dengan tab ADD TRADE")

# ==========================================
# ADD TRADE
# ==========================================
with tabs[1]:
    st.subheader("➕ ADD NEW TRADE")
    
    with st.form("entry_form", clear_on_submit=True):
        cols = st.columns(2)
        
        with cols[0]:
            buy_date = st.date_input("📅 BUY DATE", date.today())
            qty_lot = st.number_input("🔢 QTY LOT", 1, step=1)
        
        with cols[1]:
            stock_code = st.text_input("📊 STOCK CODE", "", placeholder="e.g. BBCA, BMRI").upper()
            price_buy = st.number_input("💰 BUY PRICE", 1, step=50)
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            submitted = st.form_submit_button("➕ ADD TRADE", use_container_width=True)
        
        if submitted:
            if not stock_code:
                st.error("❌ Stock code wajib diisi!")
            else:
                try:
                    # Find next empty row
                    all_values = worksheet.get_all_values()
                    next_row = 2
                    for i, row in enumerate(all_values[1:], start=2):
                        if not row[0]:
                            next_row = i
                            break
                    else:
                        next_row = len(all_values) + 1
                    
                    new_row = [
                        buy_date.strftime("%Y-%m-%d"),
                        stock_code,
                        qty_lot,
                        price_buy,
                        "", "", "", "", "",
                        "OPEN",
                        "", "", "", ""
                    ]
                    
                    with st.spinner("Saving to Google Sheets..."):
                        worksheet.insert_row(new_row, next_row, value_input_option='USER_ENTERED')
                        st.cache_data.clear()
                        st.success(f"✅ {stock_code} berhasil ditambahkan!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# ==========================================
# UPDATE
# ==========================================
with tabs[2]:
    st.subheader("✏️ UPDATE TRADE")
    
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
                
                st.info(f"**Editing:** {row['Stock Code']} - Buy: {format_rupiah(row['Price (Buy)'])}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    current_pos = row['Possition']
                    if 'Open' in str(current_pos) or 'Floating' in str(current_pos):
                        pos_index = 0
                    else:
                        pos_index = 1
                    
                    new_position = st.selectbox(
                        "📍 Update Position",
                        ["OPEN", "CLOSE"],
                        index=pos_index
                    )
                
                with col2:
                    default_date = row['Custom Date'] if pd.notna(row['Custom Date']) else date.today()
                    custom_date = st.date_input("📅 Custom Date (Scenario)", default_date)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 UPDATE", use_container_width=True):
                        try:
                            with st.spinner("Updating..."):
                                worksheet.update(f'J{gsheet_row}', [[new_position]], value_input_option='USER_ENTERED')
                                worksheet.update(f'H{gsheet_row}', [[custom_date.strftime("%Y-%m-%d")]], value_input_option='USER_ENTERED')
                                
                                st.cache_data.clear()
                                st.success("✅ Updated successfully!")
                                time.sleep(1)
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                with col2:
                    if st.button("❌ CANCEL", use_container_width=True):
                        st.rerun()
        else:
            st.info("No transactions to update")
    else:
        st.info("No transactions yet")

# ==========================================
# ANALYTICS
# ==========================================
with tabs[3]:
    st.subheader("📈 ANALYTICS DASHBOARD")
    
    if not df.empty:
        df_open = df[df['Possition'].str.contains('Open|Floating', case=False, na=False)]
        
        if not df_open.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📊 P&L Distribution")
                fig = go.Figure()
                colors = [theme['positive'] if x > 0 else theme['negative'] for x in df_open['P&L']]
                
                fig.add_trace(go.Bar(
                    x=df_open['Stock Code'],
                    y=df_open['P&L'],
                    marker_color=colors,
                    text=df_open['P&L'].apply(lambda x: format_rupiah(x)),
                    textposition='outside',
                    textfont=dict(size=10, color=theme['text'])
                ))
                
                fig.update_layout(
                    template="plotly_dark",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=theme['text']),
                    height=350,
                    margin=dict(l=20, r=20, t=20, b=20),
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 🎯 Win/Loss Ratio")
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
                        template="plotly_dark",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color=theme['text']),
                        height=350,
                        margin=dict(l=20, r=20, t=20, b=20)
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
            st.info("No open positions for analytics")
    else:
        st.info("Add trades to see analytics")

# ==========================================
# DELETE
# ==========================================
with tabs[4]:
    st.subheader("🗑️ DELETE TRADE")
    
    if not df.empty:
        options = [
            f"{row['Stock Code']} - {row['Buy Date'].strftime('%d/%m/%y') if pd.notna(row['Buy Date']) else '-'} - {format_rupiah(row['Value (Buy)'])}" 
            for _, row in df.iterrows()
        ]
        
        if options:
            to_delete = st.selectbox("Select trade to delete:", options)
            
            if to_delete:
                idx = options.index(to_delete)
                row = df.iloc[idx]
                gsheet_row = idx + 2
                
                st.warning(f"⚠️ PERMANENT DELETE: **{row['Stock Code']}**")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ CONFIRM DELETE", use_container_width=True):
                        try:
                            with st.spinner("Deleting..."):
                                worksheet.delete_rows(gsheet_row)
                                st.cache_data.clear()
                                st.success("✅ Deleted!")
                                time.sleep(1)
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                with col2:
                    if st.button("❌ CANCEL", use_container_width=True):
                        st.rerun()
        else:
            st.info("No trades to delete")
    else:
        st.info("No trades yet")

# ==========================================
# ALL TRADES
# ==========================================
with tabs[5]:
    st.subheader("📋 ALL TRADES")
    
    if not df.empty:
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            position_filter = st.multiselect(
                "Position",
                options=['OPEN', 'CLOSE'],
                default=['OPEN', 'CLOSE']
            )
        
        with col2:
            stock_filter = st.multiselect(
                "Stock",
                options=df['Stock Code'].unique().tolist()
            )
        
        with col3:
            sort_by = st.selectbox(
                "Sort by",
                ['Buy Date', 'P&L', 'Change %', 'Stock Code']
            )
        
        with col4:
            st.write("")
            st.write("")
            if st.button("🔄 Refresh", use_container_width=True, key="refresh_all"):
                st.cache_data.clear()
                st.rerun()
        
        # Apply filters
        filtered_df = df.copy()
        
        if position_filter:
            filtered_df = filtered_df[filtered_df['Possition'].isin(position_filter)]
        
        if stock_filter:
            filtered_df = filtered_df[filtered_df['Stock Code'].isin(stock_filter)]
        
        # Sort
        filtered_df = filtered_df.sort_values(by=sort_by, ascending=False)
        
        st.markdown(f"**Showing {len(filtered_df)} trades**")
        
        # Display
        display_cols = ['Buy Date', 'Stock Code', 'Qty Lot', 'Price (Buy)', 'Value (Buy)', 
                        'Possition', 'Current Price', 'Change %', 'P&L']
        df_display = filtered_df[display_cols].copy()
        
        df_display['Buy Date'] = df_display['Buy Date'].apply(lambda x: x.strftime('%d/%m/%y') if pd.notna(x) else '-')
        df_display['Price (Buy)'] = df_display['Price (Buy)'].apply(format_rupiah)
        df_display['Value (Buy)'] = df_display['Value (Buy)'].apply(format_rupiah)
        df_display['Current Price'] = df_display['Current Price'].apply(format_rupiah)
        df_display['P&L'] = df_display['P&L'].apply(format_rupiah)
        df_display['Change %'] = df_display['Change %'].apply(lambda x: f"{x:.1f}%")
        
        df_display = df_display.rename(columns={
            "Buy Date": "📅 DATE",
            "Stock Code": "📊 STOCK",
            "Qty Lot": "🔢 LOT",
            "Price (Buy)": "💰 BUY",
            "Value (Buy)": "💵 VALUE",
            "Possition": "📍 POS",
            "Current Price": "💹 CURRENT",
            "Change %": "📈 %",
            "P&L": "💲 P&L"
        })

        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            height=500
        )
        
        # Download button
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"idx_trades_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        st.info("No trades yet")

# -----------------------------------------------------------------
# FOOTER
# -----------------------------------------------------------------
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"📊 Total Trades: {len(df) if not df.empty else 0}")
with col2:
    st.caption(f"📈 Total Stocks: {df['Stock Code'].nunique() if not df.empty else 0}")
with col3:
    st.caption(f"⚡ Last Update: {datetime.now().strftime('%H:%M:%S')}")
