import streamlit as st
import gspread
import pandas as pd
import plotly.graph_objects as go
from datetime import date, datetime
import numpy as np

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
# CSS KORPORAT & MOBILE FRIENDLY
# -----------------------------------------------------------------
st.markdown("""
    <style>
    /* MAIN BACKGROUND - DARK ABU TUA KORPORAT */
    .stApp {
        background: linear-gradient(135deg, #2C3E50 0%, #34495E 50%, #2C3E50 100%);
    }
    
    /* KONTENER UTAMA */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 1400px !important;
        margin: 0 auto !important;
    }
    
    /* HEADER KORPORAT */
    .premium-header {
        background: rgba(44, 62, 80, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 30px;
        padding: 0.8rem 2rem;
        margin-bottom: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    
    .header-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ECF0F1;
        letter-spacing: -0.02em;
    }
    
    .header-title span {
        color: #3498DB;
        font-weight: 300;
    }
    
    .header-date {
        color: #BDC3C7;
        font-size: 0.9rem;
        background: rgba(52, 73, 94, 0.5);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    /* TABS KORPORAT */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(52, 73, 94, 0.5);
        backdrop-filter: blur(10px);
        padding: 4px;
        border-radius: 40px;
        border: 1px solid rgba(255,255,255,0.03);
        margin-bottom: 1.5rem;
        flex-wrap: nowrap;
        overflow-x: auto;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 30px;
        padding: 0.5rem 1.2rem !important;
        color: #BDC3C7;
        font-weight: 500;
        font-size: 0.9rem !important;
        transition: all 0.3s ease;
        white-space: nowrap;
        border: 1px solid transparent;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #ECF0F1;
        background: rgba(255,255,255,0.02);
        border-color: rgba(255,255,255,0.05);
    }
    
    .stTabs [aria-selected="true"] {
        background: #3498DB !important;
        color: white !important;
        box-shadow: 0 4px 10px rgba(52,152,219,0.3);
    }
    
    /* METRIC CARDS KORPORAT */
    div[data-testid="metric-container"] {
        background: rgba(52, 73, 94, 0.3) !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 16px !important;
        padding: 1rem !important;
        backdrop-filter: blur(8px);
        transition: all 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        border-color: #3498DB !important;
        background: rgba(52, 73, 94, 0.5) !important;
    }
    
    div[data-testid="metric-container"] label {
        color: #95A5A6 !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    
    div[data-testid="metric-container"] div {
        color: #ECF0F1 !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
    }
    
    /* DATAFRAME KORPORAT - TIDAK SILAU */
    .stDataFrame {
        background: rgba(44, 62, 80, 0.3);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.03);
        border-radius: 16px;
        overflow: hidden;
    }
    
    .stDataFrame [data-testid="stDataFrame"] {
        background: transparent !important;
    }
    
    .stDataFrame table {
        border-collapse: separate;
        border-spacing: 0;
        width: 100%;
        background: transparent !important;
    }
    
    .stDataFrame th {
        background: rgba(52, 73, 94, 0.6) !important;
        color: #ECF0F1 !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.8rem 1rem !important;
        border-bottom: 2px solid #3498DB !important;
    }
    
    .stDataFrame td {
        background: rgba(44, 62, 80, 0.2) !important;
        color: #BDC3C7 !important;
        padding: 0.6rem 1rem !important;
        border-bottom: 1px solid rgba(255,255,255,0.02) !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease;
    }
    
    .stDataFrame tr:hover td {
        background: rgba(52, 73, 94, 0.4) !important;
    }
    
    /* BUTTON KORPORAT */
    .stButton>button {
        background: #3498DB;
        color: white;
        border: none;
        border-radius: 30px !important;
        padding: 0.4rem 1.5rem !important;
        font-weight: 500;
        font-size: 0.85rem !important;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: #2980B9;
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(52,152,219,0.3);
    }
    
    /* INPUT FIELDS KORPORAT */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        background: rgba(52, 73, 94, 0.3) !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 30px !important;
        transition: all 0.3s ease;
    }
    
    div[data-baseweb="input"]:hover, div[data-baseweb="select"]:hover {
        border-color: #3498DB !important;
        background: rgba(52, 73, 94, 0.5) !important;
    }
    
    input, select {
        color: #ECF0F1 !important;
        font-size: 0.9rem !important;
        padding: 0.6rem 1rem !important;
    }
    
    .stTextInput label, .stSelectbox label, .stDateInput label {
        color: #95A5A6 !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        margin-bottom: 0.2rem !important;
    }
    
    /* DIVIDER KORPORAT */
    hr {
        background: linear-gradient(90deg, transparent, #3498DB, transparent) !important;
        height: 1px !important;
        border: none !important;
        margin: 1.5rem 0 !important;
        opacity: 0.3;
    }
    
    /* SCROLLBAR KORPORAT */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(52, 73, 94, 0.3);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #3498DB;
        border-radius: 10px;
    }
    
    /* ===== MOBILE RESPONSIVENESS (KHUSUS HP) ===== */
    @media (max-width: 768px) {
        h1 { font-size: 1.8rem !important; }
        h2 { font-size: 1.4rem !important; }
        h3 { font-size: 1.1rem !important; }
        
        .premium-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
        }
        
        div[data-testid="metric-container"] {
            padding: 12px !important;
            margin-bottom: 10px !important;
        }
        div[data-testid="metric-container"] div {
            font-size: 1.2rem !important;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
            gap: 15px !important;
            padding-bottom: 5px !important;
        }
        .stTabs [data-baseweb="tab"] {
            white-space: nowrap !important;
            font-size: 0.85rem !important;
            padding: 8px 12px !important;
        }
        
        .stDataFrame {
            overflow-x: auto !important;
        }
        .stDataFrame table {
            min-width: 800px !important; 
        }
        
        .stButton>button {
            padding: 8px 16px !important;
            font-size: 0.9rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------
# HEADER KORPORAT
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

# -----------------------------------------------------------------
# KONEKSI GOOGLE SHEETS
# -----------------------------------------------------------------
# Sesuai dengan kolom di GSheet
COLUMNS = [
    "Buy Date", "Stock Code", "Qty Lot", "Price (Buy)", "Value (Buy)", 
    "Current Date", "Current Price", "Custom Date", "Custom Price", 
    "Possition", "Change %", "P&L", "Change % (Custom)", "P&L (Custom)"
]

@st.cache_resource(ttl=300)
def get_gsheet_client():
    try:
        # PERBAIKAN 1: Metode otentikasi baru untuk Streamlit Cloud agar tidak error "_auth_request"
        creds_dict = dict(st.secrets["gcp_service_account"])
        client = gspread.service_account_from_dict(creds_dict)
        return client
    except Exception as e:
        st.error(f"🔴 Gagal koneksi ke Google Sheets: {str(e)}")
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

# Initialize
client = get_gsheet_client()
if client:
    worksheet, df = load_data(client)
else:
    st.stop()

# Format function untuk separator ribuan
def format_rupiah(angka):
    if pd.isna(angka) or angka == 0:
        return "Rp 0"
    return f"Rp {angka:,.0f}".replace(',', '.')

# =========================================================================
# TABS
# =========================================================================
tabs = st.tabs(["📊 DASHBOARD", "➕ ENTRY", "✏️ UPDATE", "📈 ANALYTICS", "🗑️ DELETE"])

# ==========================================
# DASHBOARD
# ==========================================
with tabs[0]:
    if not df.empty:
        # Filter open positions
        df_open = df[df['Possition'].str.contains('Open|Floating', case=False, na=False)]
        
        # METRICS
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
        
        # TABEL TRANSACTIONS
        st.subheader("📋 TRANSACTION HISTORY")
        
        display_cols = ['Buy Date', 'Stock Code', 'Qty Lot', 'Price (Buy)', 'Value (Buy)', 
                        'Possition', 'Current Price', 'Change %', 'P&L']
        df_display = df[display_cols].copy()
        
        # Format dates & Hindari Error NaT
        df_display['Buy Date'] = df_display['Buy Date'].apply(lambda x: x.strftime('%d/%m/%y') if pd.notna(x) else '-')
        
        # Format numbers dengan separator ribuan
        df_display['Price (Buy)'] = df_display['Price (Buy)'].apply(lambda x: f"Rp {x:,.0f}".replace(',', '.'))
        df_display['Value (Buy)'] = df_display['Value (Buy)'].apply(lambda x: f"Rp {x:,.0f}".replace(',', '.'))
        df_display['Current Price'] = df_display['Current Price'].apply(lambda x: f"Rp {x:,.0f}".replace(',', '.'))
        df_display['P&L'] = df_display['P&L'].apply(lambda x: f"Rp {x:,.0f}".replace(',', '.'))
        df_display['Change %'] = df_display['Change %'].apply(lambda x: f"{x:.1f}%")
        
        # Rename kolom agar rapi
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

        # PERBAIKAN: Fungsi pewarnaan kolom P&L dengan Pandas Styler
        def color_profit_loss(val):
            try:
                clean_val = str(val).replace('Rp', '').replace('%', '').replace('.', '').replace(',', '').strip()
                num = float(clean_val)
                if num > 0:
                    return 'color: #2ECC71; font-weight: 700;'
                elif num < 0:
                    return 'color: #E74C3C; font-weight: 700;'
                else:
                    return 'color: #BDC3C7;'
            except:
                return ''

        try:
            styled_df = df_display.style.map(color_profit_loss, subset=['📈 CHANGE', '💲 P&L'])
        except:
            styled_df = df_display.style.applymap(color_profit_loss, subset=['📈 CHANGE', '💲 P&L'])

        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # SUMMARY
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
                        buy_date.strftime("%Y-%m-%d"), stock_code, qty_lot, price_buy,
                        "", "", "", "", "", position, "", "", "", ""
                    ]
                    
                    with st.spinner("Menyimpan ke Google Sheets..."):
                        # PERBAIKAN 2: Anti Ghost Rows (Cari baris kosong di kolom B lalu timpa)
                        kolom_b = worksheet.col_values(2) # Ambil isi kolom B (Stock Code)
                        baris_baru = len(kolom_b) + 1
                        
                        worksheet.update(
                            range_name=f"A{baris_baru}", 
                            values=[new_row], 
                            value_input_option='USER_ENTERED'
                        )
                        
                        st.cache_data.clear()
                        st.success(f"✅ {stock_code} berhasil ditambahkan!")
                        st.balloons()
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# ==========================================
# UPDATE - Edit
# ==========================================
with tabs[2]:
    st.subheader("✏️ UPDATE TRANSACTION")
    
    if not df.empty:
        # PERBAIKAN 3: Anti error tanggal NaT saat load ke Selectbox
        options = [
            f"{row['Stock Code']} - {row['Buy Date'].strftime('%d/%m/%y') if pd.notna(row['Buy Date']) else '-'} - {format_rupiah(row['Price (Buy)'])}" 
            for _, row in df.iterrows()
        ]
        selected = st.selectbox("Pilih transaksi:", options)
        
        if selected:
            idx = options.index(selected)
            row = df.iloc[idx]
            gsheet_row = idx + 2  # +2 karena header di baris 1
            
            st.info(f"**Mengedit:** {row['Stock Code']} - Beli: {format_rupiah(row['Price (Buy)'])}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_position = st.selectbox(
                    "📍 Update Position",
                    ["Open/Floating", "Closed"],
                    index=0 if 'Open' in str(row['Possition']) else 1
                )
            
            with col2:
                custom_date = st.date_input(
                    "📅 Custom Date (Skenario)",
                    value=row['Custom Date'] if pd.notna(row['Custom Date']) else date.today()
                )
            
            if st.button("🔄 UPDATE", use_container_width=True):
                try:
                    with st.spinner("Updating..."):
                        updates = [
                            {'range': f'J{gsheet_row}', 'values': [[new_position]]},  
                            {'range': f'H{gsheet_row}', 'values': [[custom_date.strftime("%Y-%m-%d")]]}  
                        ]
                        worksheet.batch_update(updates, value_input_option='USER_ENTERED')
                        st.cache_data.clear()
                        st.success("✅ Data berhasil diupdate!")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
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
                # Bar Chart P&L
                fig = go.Figure()
                colors = ['#2ECC71' if x > 0 else '#E74C3C' for x in df_open['P&L']]
                
                fig.add_trace(go.Bar(
                    x=df_open['Stock Code'],
                    y=df_open['P&L'],
                    marker_color=colors,
                    text=df_open['P&L'].apply(lambda x: f'Rp {x:,.0f}'),
                    textposition='outside',
                    textfont=dict(size=10)
                ))
                
                fig.update_layout(
                    title="📊 P&L per Saham",
                    template="plotly_dark",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=300,
                    margin=dict(l=20, r=20, t=40, b=20),
                    showlegend=False,
                    yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Pie Chart Win/Loss
                wins = (df_open['P&L'] > 0).sum()
                losses = (df_open['P&L'] < 0).sum()
                
                if wins + losses > 0:
                    fig = go.Figure(data=[go.Pie(
                        labels=['WIN', 'LOSS'],
                        values=[wins, losses],
                        marker_colors=['#2ECC71', '#E74C3C'],
                        textinfo='label+percent',
                        textfont=dict(size=12),
                        hole=0.4,
                        pull=[0.02, 0]
                    )])
                    
                    fig.update_layout(
                        title="🎯 Win/Loss Ratio",
                        template="plotly_dark",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        height=300,
                        margin=dict(l=20, r=20, t=40, b=20),
                        annotations=[dict(
                            text=f'{wins+losses} Trades',
                            x=0.5, y=0.5,
                            font=dict(size=12, color='white')
                        )]
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Risk Metrics
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
        # PERBAIKAN 4: Anti error tanggal NaT saat load ke Selectbox
        options = [
            f"{row['Stock Code']} - {row['Buy Date'].strftime('%d/%m/%y') if pd.notna(row['Buy Date']) else '-'} - {format_rupiah(row['Value (Buy)'])}" 
            for _, row in df.iterrows()
        ]
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
                        with st.spinner("Deleting..."):
                            # PERBAIKAN 5: Menggunakan delete_row() BUKAN delete_rows()
                            worksheet.delete_row(gsheet_row)
                            st.cache_data.clear()
                            st.success("✅ Transaksi dihapus!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            with col2:
                if st.button("BATAL", use_container_width=True):
                    st.rerun()
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
