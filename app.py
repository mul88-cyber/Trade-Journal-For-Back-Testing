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
    page_title="AlphaStock Pro", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------
# PREMIUM CSS - ELEGAN & KOMPAK
# -----------------------------------------------------------------
st.markdown("""
    <style>
    /* MAIN BACKGROUND PREMIUM */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1E1A3A, #0B0F1C 80%);
    }
    
    /* KONTENER UTAMA LEBIH RAPI */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 1400px !important;
        margin: 0 auto !important;
    }
    
    /* HEADER ELEGAN */
    .premium-header {
        background: rgba(15, 23, 42, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 30px;
        padding: 0.8rem 2rem;
        margin-bottom: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .header-title {
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #818CF8, #C084FC, #F472B6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
    }
    
    .header-date {
        color: #94A3B8;
        font-size: 0.9rem;
        background: rgba(255,255,255,0.03);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    /* TABS PREMIUM - LEBIH KOMPAK */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(15, 23, 42, 0.5);
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
        color: #94A3B8;
        font-weight: 600;
        font-size: 0.9rem !important;
        transition: all 0.3s ease;
        white-space: nowrap;
        border: 1px solid transparent;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: white;
        background: rgba(255,255,255,0.02);
        border-color: rgba(255,255,255,0.05);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3B82F6, #8B5CF6) !important;
        color: white !important;
        box-shadow: 0 8px 20px -8px #3B82F6;
    }
    
    /* METRIC CARDS PREMIUM - KOMPAK */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(96, 165, 250, 0.08), rgba(167, 139, 250, 0.08)) !important;
        border: 1px solid rgba(96, 165, 250, 0.15) !important;
        border-radius: 24px !important;
        padding: 1rem !important;
        backdrop-filter: blur(8px);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    div[data-testid="metric-container"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
        transition: left 0.5s ease;
    }
    
    div[data-testid="metric-container"]:hover::before {
        left: 100%;
    }
    
    div[data-testid="metric-container"] label {
        color: #94A3B8 !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    
    div[data-testid="metric-container"] div {
        background: linear-gradient(135deg, #F0F9FF, #E2E8F0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
    }
    
    /* DATAFRAME PREMIUM dengan COLOR SCALE */
    .stDataFrame {
        background: rgba(15, 23, 42, 0.3);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.03);
        border-radius: 24px;
        overflow: hidden;
    }
    
    .stDataFrame table {
        border-collapse: separate;
        border-spacing: 0;
        width: 100%;
    }
    
    .stDataFrame th {
        background: rgba(59, 130, 246, 0.15) !important;
        color: #F0F9FF !important;
        font-weight: 700 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.8rem 1rem !important;
        border-bottom: 2px solid rgba(59, 130, 246, 0.2) !important;
    }
    
    .stDataFrame td {
        color: #CBD5E1 !important;
        padding: 0.6rem 1rem !important;
        border-bottom: 1px solid rgba(255,255,255,0.02) !important;
        font-size: 0.9rem !important;
    }
    
    .stDataFrame tr:hover td {
        background: rgba(59, 130, 246, 0.08) !important;
    }
    
    /* BUTTON PREMIUM - KOMPAK */
    .stButton>button {
        background: linear-gradient(135deg, #3B82F6, #8B5CF6);
        color: white;
        border: none;
        border-radius: 40px !important;
        padding: 0.4rem 1.5rem !important;
        font-weight: 600;
        font-size: 0.85rem !important;
        box-shadow: 0 8px 20px -8px #3B82F6;
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 25px -8px #3B82F6;
    }
    
    /* INPUT FIELDS PREMIUM */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        background: rgba(30, 41, 59, 0.4) !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 40px !important;
        transition: all 0.3s ease;
        backdrop-filter: blur(4px);
    }
    
    div[data-baseweb="input"]:hover, div[data-baseweb="select"]:hover {
        border-color: #3B82F6 !important;
        background: rgba(30, 41, 59, 0.6) !important;
    }
    
    input, select {
        color: #F0F9FF !important;
        font-size: 0.9rem !important;
        padding: 0.6rem 1rem !important;
    }
    
    .stTextInput label, .stSelectbox label, .stDateInput label {
        color: #94A3B8 !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        margin-bottom: 0.2rem !important;
    }
    
    /* FORM HORIZONTAL PREMIUM */
    .premium-form {
        background: rgba(15, 23, 42, 0.4);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.03);
        border-radius: 50px;
        padding: 0.8rem 1.5rem;
        margin-bottom: 1.5rem;
        display: flex;
        gap: 1rem;
        align-items: center;
        flex-wrap: wrap;
    }
    
    /* DIVIDER PREMIUM */
    hr {
        background: linear-gradient(90deg, transparent, #3B82F6, #8B5CF6, #3B82F6, transparent) !important;
        height: 2px !important;
        border: none !important;
        margin: 1.5rem 0 !important;
        opacity: 0.3;
    }
    
    /* SCROLLBAR PREMIUM */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.5);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #3B82F6, #8B5CF6);
        border-radius: 10px;
    }
    
    /* ANIMATIONS */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .element-container {
        animation: fadeIn 0.4s ease-out;
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
    // COLOR SCALE PREMIUM UNTUK TABEL
    function applyPremiumColorScale() {
        const tables = document.querySelectorAll('.stDataFrame table');
        tables.forEach(table => {
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                
                // P&L Column (index 11)
                if (cells.length >= 12) {
                    const pnlCell = cells[11];
                    const pnlText = pnlCell?.textContent || '';
                    const pnlValue = parseFloat(pnlText.replace(/[^0-9-]/g, ''));
                    
                    if (!isNaN(pnlValue)) {
                        if (pnlValue > 0) {
                            pnlCell.style.background = 'linear-gradient(90deg, rgba(16, 185, 129, 0.25), rgba(16, 185, 129, 0.05))';
                            pnlCell.style.color = '#A7F3D0';
                            pnlCell.style.fontWeight = '700';
                            pnlCell.style.textShadow = '0 0 10px rgba(16,185,129,0.3)';
                        } else if (pnlValue < 0) {
                            pnlCell.style.background = 'linear-gradient(90deg, rgba(239, 68, 68, 0.25), rgba(239, 68, 68, 0.05))';
                            pnlCell.style.color = '#FECACA';
                            pnlCell.style.fontWeight = '700';
                            pnlCell.style.textShadow = '0 0 10px rgba(239,68,68,0.3)';
                        }
                    }
                }
                
                // Change % Column (index 10)
                if (cells.length >= 11) {
                    const changeCell = cells[10];
                    const changeText = changeCell?.textContent || '';
                    const changeValue = parseFloat(changeText.replace(/[^0-9.-]/g, ''));
                    
                    if (!isNaN(changeValue)) {
                        if (changeValue > 0) {
                            changeCell.style.color = '#A7F3D0';
                            changeCell.style.fontWeight = '600';
                        } else if (changeValue < 0) {
                            changeCell.style.color = '#FECACA';
                            changeCell.style.fontWeight = '600';
                        }
                    }
                }
            });
        });
    }
    
    // Run on load and observe changes
    document.addEventListener('DOMContentLoaded', applyPremiumColorScale);
    const observer = new MutationObserver(applyPremiumColorScale);
    observer.observe(document.body, { childList: true, subtree: true });
    </script>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------
# HEADER PREMIUM
# -----------------------------------------------------------------
st.markdown(f"""
    <div class="premium-header">
        <div class="header-title">✨ AlphaStock Professional</div>
        <div class="header-date">
            <span>📅 {datetime.now().strftime('%A, %d %B %Y')}</span>
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

COLUMNS = [
    "Buy Date", "Stock Code", "Qty Lot", "Price (Buy)", "Value (Buy)", 
    "Current Date", "Current Price", "Custom Date", "Custom Price", 
    "Position", "Change %", "P&L", "Change % (Custom)", "P&L (Custom)"
]

@st.cache_resource(ttl=300)
def get_gsheet_client():
    try:
        creds_dict = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"🔴 Gagal koneksi: {str(e)}")
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
            
        df = pd.DataFrame(data[1:], columns=COLUMNS[:len(data[0])])
        df = df[df['Stock Code'].astype(str).str.strip() != '']
        
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

        numeric_cols = ["Price (Buy)", "Value (Buy)", "Current Price", "Custom Price", 
                       "P&L", "P&L (Custom)", "Change %", "Change % (Custom)", "Qty Lot"]
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].apply(clean_number)
        
        date_cols = ["Buy Date", "Current Date", "Custom Date"]
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return worksheet, df
    except Exception as e:
        st.error(f"🔴 Gagal load: {str(e)}")
        return None, pd.DataFrame()

# Initialize
client = get_gsheet_client()
if client:
    worksheet, df = load_data(client)
else:
    st.stop()

# =========================================================================
# TABS PREMIUM
# =========================================================================
tabs = st.tabs(["📊 DASHBOARD", "➕ ENTRY", "✏️ UPDATE", "📈 ANALYTICS", "🗑️ DELETE"])

# ==========================================
# DASHBOARD PREMIUM
# ==========================================
with tabs[0]:
    if not df.empty:
        df_open = df[df['Position'].str.contains('Open|Floating', case=False, na=False)]
        
        # METRICS PREMIUM
        cols = st.columns(4)
        with cols[0]:
            st.metric("TOTAL PORTFOLIO", f"Rp {df_open['Value (Buy)'].sum():,.0f}")
        with cols[1]:
            pnl = df_open['P&L'].sum()
            st.metric("REALIZED P&L", f"Rp {pnl:,.0f}", 
                     delta=f"{pnl/df_open['Value (Buy)'].sum()*100:.1f}%" if df_open['Value (Buy)'].sum() > 0 else None)
        with cols[2]:
            win_rate = (df_open[df_open['P&L'] > 0].shape[0] / df_open.shape[0] * 100) if not df_open.empty else 0
            st.metric("WIN RATE", f"{win_rate:.1f}%")
        with cols[3]:
            st.metric("ACTIVE POSITIONS", f"{len(df_open)}")
        
        st.divider()
        
        # TABLE PREMIUM dengan COLOR SCALE
        st.subheader("📋 TRANSACTIONS")
        
        display_cols = ['Buy Date', 'Stock Code', 'Qty Lot', 'Price (Buy)', 'Position', 'Change %', 'P&L']
        df_display = df[display_cols].copy()
        df_display['Buy Date'] = df_display['Buy Date'].dt.strftime('%d/%m/%y')
        df_display['Change %'] = df_display['Change %'].round(1)
        df_display['P&L'] = df_display['P&L'].round(0)
        
        st.dataframe(
            df_display,
            use_container_width=True,
            column_config={
                "Buy Date": "DATE",
                "Stock Code": "STOCK",
                "Qty Lot": "LOT",
                "Price (Buy)": st.column_config.NumberColumn("BUY PRICE", format="Rp %d"),
                "Position": "POS",
                "Change %": st.column_config.NumberColumn("CHG %", format="%.1f %%"),
                "P&L": st.column_config.NumberColumn("P&L", format="Rp %d"),
            },
            hide_index=True,
            height=350
        )
    else:
        st.info("✨ Belum ada transaksi. Mulai dengan tab ENTRY")

# ==========================================
# ENTRY PREMIUM - HORIZONTAL
# ==========================================
with tabs[1]:
    st.subheader("➕ NEW TRANSACTION")
    
    with st.form("premium_entry", clear_on_submit=True):
        cols = st.columns([1.2, 1, 0.8, 1.2, 1, 0.8])
        
        with cols[0]:
            date_input = st.date_input("DATE", date.today(), label_visibility="collapsed")
        with cols[1]:
            stock_input = st.text_input("STOCK", "", placeholder="BBCA", label_visibility="collapsed").upper()
        with cols[2]:
            lot_input = st.number_input("LOT", 1, step=1, label_visibility="collapsed")
        with cols[3]:
            price_input = st.number_input("PRICE", 1, step=10, label_visibility="collapsed")
        with cols[4]:
            pos_input = st.selectbox("POS", ["OPEN", "CLOSED"], label_visibility="collapsed")
        with cols[5]:
            submitted = st.form_submit_button("➕ ADD", use_container_width=True)
        
        if submitted:
            if not stock_input:
                st.error("❌ Stock code required")
            else:
                try:
                    new_row = [
                        date_input.strftime("%Y-%m-%d"),
                        stock_input,
                        lot_input,
                        price_input,
                        "", "", "", "", "",
                        "Open/Floating" if pos_input == "OPEN" else "Closed",
                        "", "", "", ""
                    ]
                    worksheet.append_row(new_row, value_input_option='USER_ENTERED')
                    st.cache_data.clear()
                    st.success(f"✅ {stock_input} added successfully")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# ==========================================
# UPDATE PREMIUM
# ==========================================
with tabs[2]:
    st.subheader("✏️ UPDATE POSITION")
    
    if not df.empty:
        options = [f"{row['Stock Code']} • {row['Buy Date'].strftime('%d/%b')} • Rp {row['Price (Buy)']:,.0f}" 
                  for _, row in df.iterrows()]
        selected = st.selectbox("SELECT TRANSACTION", options)
        
        if selected:
            idx = options.index(selected)
            row = df.iloc[idx]
            gsheet_row = idx + 2
            
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                new_pos = st.selectbox("POSITION", ["Open/Floating", "Closed"],
                                      index=0 if 'Open' in row['Position'] else 1)
            with col2:
                custom_date = st.date_input("CUSTOM DATE", date.today())
            with col3:
                if st.button("UPDATE", use_container_width=True):
                    try:
                        updates = [
                            {'range': f'J{gsheet_row}', 'values': [[new_pos]]},
                            {'range': f'H{gsheet_row}', 'values': [[custom_date.strftime("%Y-%m-%d")]]}
                        ]
                        worksheet.batch_update(updates, value_input_option='USER_ENTERED')
                        st.cache_data.clear()
                        st.success("✅ Updated")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    else:
        st.info("No transactions yet")

# ==========================================
# ANALYTICS PREMIUM
# ==========================================
with tabs[3]:
    st.subheader("📈 PORTFOLIO ANALYTICS")
    
    if not df.empty and not df[df['Position'].str.contains('Open', na=False)].empty:
        df_open = df[df['Position'].str.contains('Open', na=False)]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar Chart Premium
            fig = go.Figure()
            colors = ['#10B981' if x > 0 else '#EF4444' for x in df_open['P&L']]
            
            fig.add_trace(go.Bar(
                x=df_open['Stock Code'],
                y=df_open['P&L'],
                marker_color=colors,
                text=df_open['P&L'].apply(lambda x: f'Rp {x:,.0f}'),
                textposition='outside',
                textfont=dict(color='white', size=10)
            ))
            
            fig.update_layout(
                title="📊 P&L by Stock",
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
            # Pie Chart Premium
            wins = (df_open['P&L'] > 0).sum()
            losses = (df_open['P&L'] < 0).sum()
            
            fig = go.Figure(data=[go.Pie(
                labels=['WINNING', 'LOSING'],
                values=[wins, losses],
                marker_colors=['#10B981', '#EF4444'],
                textinfo='label+percent',
                textfont=dict(size=12, color='white'),
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
                annotations=[dict(text=f'{wins+losses} Total', x=0.5, y=0.5, font=dict(size=14))]
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No active positions for analytics")

# ==========================================
# DELETE PREMIUM
# ==========================================
with tabs[4]:
    st.subheader("🗑️ DELETE TRANSACTION")
    
    if not df.empty:
        options = [f"{row['Stock Code']} • {row['Buy Date'].strftime('%d/%b/%y')} • Rp {row['Value (Buy)']:,.0f}" 
                  for _, row in df.iterrows()]
        to_delete = st.selectbox("SELECT TO DELETE", options)
        
        if to_delete:
            idx = options.index(to_delete)
            row = df.iloc[idx]
            gsheet_row = idx + 2
            
            st.warning(f"⚠️ Permanent deletion of **{row['Stock Code']}**")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ CONFIRM DELETE", use_container_width=True, type="primary"):
                    try:
                        worksheet.delete_rows(gsheet_row)
                        st.cache_data.clear()
                        st.success("✅ Deleted")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            with col2:
                if st.button("CANCEL", use_container_width=True):
                    st.rerun()
    else:
        st.info("No transactions to delete")

# -----------------------------------------------------------------
# FOOTER PREMIUM
# -----------------------------------------------------------------
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"💼 {len(df) if not df.empty else 0} Transactions")
with col2:
    st.caption(f"📊 {df['Stock Code'].nunique() if not df.empty else 0} Stocks")
with col3:
    st.caption(f"⚡ AlphaStock Pro v3.0")
