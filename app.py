import streamlit as st
import gspread
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime
from google.oauth2.service_account import Credentials
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
# DARK ABU-ABU TUA KORPORAT CSS
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
    
    /* DATAFRAME KORPORAT dengan COLOR SCALE */
    .stDataFrame {
        background: rgba(44, 62, 80, 0.3);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.03);
        border-radius: 16px;
        overflow: hidden;
    }
    
    .stDataFrame table {
        border-collapse: separate;
        border-spacing: 0;
        width: 100%;
    }
    
    .stDataFrame th {
        background: rgba(52, 73, 94, 0.5) !important;
        color: #ECF0F1 !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.8rem 1rem !important;
        border-bottom: 2px solid #3498DB !important;
    }
    
    .stDataFrame td {
        color: #BDC3C7 !important;
        padding: 0.6rem 1rem !important;
        border-bottom: 1px solid rgba(255,255,255,0.02) !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease;
    }
    
    .stDataFrame tr:hover td {
        background: rgba(52, 73, 94, 0.3) !important;
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
    
    /* MOBILE RESPONSIVE */
    @media (max-width: 768px) {
        .premium-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.4rem 1rem !important;
            font-size: 0.8rem !important;
        }
        
        div[data-testid="metric-container"] div {
            font-size: 1.2rem !important;
        }
    }
    </style>
    
    <script>
    // COLOR SCALE UNTUK TABEL
    function applyColorScale() {
        const tables = document.querySelectorAll('.stDataFrame table');
        tables.forEach(table => {
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                
                // Kolom P&L (index 11)
                if (cells.length >= 12) {
                    const pnlCell = cells[11];
                    const pnlText = pnlCell?.textContent || '';
                    const pnlValue = parseFloat(pnlText.replace(/[^0-9-]/g, ''));
                    
                    if (!isNaN(pnlValue)) {
                        if (pnlValue > 0) {
                            pnlCell.style.background = 'linear-gradient(90deg, rgba(46, 204, 113, 0.2), rgba(46, 204, 113, 0.05))';
                            pnlCell.style.color = '#2ECC71';
                            pnlCell.style.fontWeight = '600';
                        } else if (pnlValue < 0) {
                            pnlCell.style.background = 'linear-gradient(90deg, rgba(231, 76, 60, 0.2), rgba(231, 76, 60, 0.05))';
                            pnlCell.style.color = '#E74C3C';
                            pnlCell.style.fontWeight = '600';
                        }
                    }
                }
                
                // Kolom Change % (index 10)
                if (cells.length >= 11) {
                    const changeCell = cells[10];
                    const changeText = changeCell?.textContent || '';
                    const changeValue = parseFloat(changeText.replace(/[^0-9.-]/g, ''));
                    
                    if (!isNaN(changeValue)) {
                        if (changeValue > 0) {
                            changeCell.style.color = '#2ECC71';
                            changeCell.style.fontWeight = '600';
                        } else if (changeValue < 0) {
                            changeCell.style.color = '#E74C3C';
                            changeCell.style.fontWeight = '600';
                        }
                    }
                }
            });
        });
    }
    
    document.addEventListener('DOMContentLoaded', applyColorScale);
    const observer = new MutationObserver(applyColorScale);
    observer.observe(document.body, { childList: true, subtree: true });
    </script>
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
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Sesuai dengan kolom di GSheet
COLUMNS = [
    "Buy Date", "Stock Code", "Qty Lot", "Price (Buy)", "Value (Buy)", 
    "Current Date", "Current Price", "Custom Date", "Custom Price", 
    "Possition", "Change %", "P&L", "Change % (Custom)", "P&L (Custom)"
]

@st.cache_resource(ttl=300)
def get_gsheet_client():
    try:
        creds_dict = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
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
            st.metric("💰 TOTAL PORTFOLIO", f"Rp {total_val:,.0f}")
        with cols[1]:
            pnl = df_open['P&L'].sum() if not df_open.empty else 0
            pnl_pct = (pnl/total_val*100) if total_val > 0 else 0
            st.metric("📈 UNREALIZED P&L", f"Rp {pnl:,.0f}", delta=f"{pnl_pct:.1f}%")
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
        
        # Format dates
        df_display['Buy Date'] = df_display['Buy Date'].dt.strftime('%d/%m/%y')
        
        # Format numbers
        df_display['Change %'] = df_display['Change %'].round(1)
        df_display['P&L'] = df_display['P&L'].round(0)
        
        st.dataframe(
            df_display,
            use_container_width=True,
            column_config={
                "Buy Date": "📅 DATE",
                "Stock Code": "📊 STOCK",
                "Qty Lot": "🔢 LOT",
                "Price (Buy)": st.column_config.NumberColumn("💰 BUY", format="Rp %d"),
                "Value (Buy)": st.column_config.NumberColumn("💵 VALUE", format="Rp %d"),
                "Possition": "📍 POS",
                "Current Price": st.column_config.NumberColumn("💹 CURRENT", format="Rp %d"),
                "Change %": st.column_config.NumberColumn("📈 CHG %", format="%.1f %%"),
                "P&L": st.column_config.NumberColumn("💲 P&L", format="Rp %d"),
            },
            hide_index=True,
            height=400
        )
        
        # SUMMARY
        col1, col2, col3 = st.columns(3)
        with col1:
            total_pnl = df['P&L'].sum()
            st.info(f"💰 Total Realized P&L: **Rp {total_pnl:,.0f}**")
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
                        buy_date.strftime("%Y-%m-%d"),  # Buy Date
                        stock_code,                      # Stock Code
                        qty_lot,                          # Qty Lot
                        price_buy,                        # Price (Buy)
                        "",                               # Value (Buy) - formula
                        "",                               # Current Date - formula
                        "",                               # Current Price - formula
                        "",                               # Custom Date
                        "",                               # Custom Price - formula
                        position,                         # Possition
                        "",                               # Change % - formula
                        "",                               # P&L - formula
                        "",                               # Change % (Custom) - formula
                        ""                                # P&L (Custom) - formula
                    ]
                    worksheet.append_row(new_row, value_input_option='USER_ENTERED')
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
        # Pilih transaksi
        options = [f"{row['Stock Code']} - {row['Buy Date'].strftime('%d/%m/%y')} - Rp {row['Price (Buy)']:,.0f}" 
                  for _, row in df.iterrows()]
        selected = st.selectbox("Pilih transaksi:", options)
        
        if selected:
            idx = options.index(selected)
            row = df.iloc[idx]
            gsheet_row = idx + 2  # +2 karena header di baris 1
            
            st.info(f"**Mengedit:** {row['Stock Code']} - Beli: Rp {row['Price (Buy)']:,.0f}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Update Position
                new_position = st.selectbox(
                    "📍 Update Position",
                    ["Open/Floating", "Closed"],
                    index=0 if 'Open' in str(row['Possition']) else 1
                )
            
            with col2:
                # Update Custom Date
                custom_date = st.date_input(
                    "📅 Custom Date (Skenario)",
                    value=row['Custom Date'] if pd.notna(row['Custom Date']) else date.today()
                )
            
            if st.button("🔄 UPDATE", use_container_width=True):
                try:
                    updates = [
                        {'range': f'J{gsheet_row}', 'values': [[new_position]]},  # Kolom Possition
                        {'range': f'H{gsheet_row}', 'values': [[custom_date.strftime("%Y-%m-%d")]]}  # Kolom Custom Date
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
        df_open = df[df['Possition'].str.contains('Open', na=False)]
        
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
                ))
                
                fig.update_layout(
                    title="📊 P&L per Saham",
                    template="plotly_dark",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=300,
                    margin=dict(l=20, r=20, t=40, b=20),
                    showlegend=False
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
                        hole=0.4
                    )])
                    
                    fig.update_layout(
                        title="🎯 Win/Loss Ratio",
                        template="plotly_dark",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        height=300,
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Risk Metrics
            st.divider()
            st.subheader("📊 RISK METRICS")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                volatility = df_open['Change %'].std() if len(df_open) > 1 else 0
                st.metric("Volatility", f"{volatility:.2f}%")
            with col2:
                avg_return = df_open['Change %'].mean()
                st.metric("Avg Return", f"{avg_return:.2f}%")
            with col3:
                max_loss = df_open['P&L'].min()
                st.metric("Max Loss", f"Rp {max_loss:,.0f}")
            with col4:
                max_gain = df_open['P&L'].max()
                st.metric("Max Gain", f"Rp {max_gain:,.0f}")
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
        options = [f"{row['Stock Code']} - {row['Buy Date'].strftime('%d/%m/%y')} - Rp {row['Value (Buy)']:,.0f}" 
                  for _, row in df.iterrows()]
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
