import streamlit as st
import gspread
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
from google.oauth2.service_account import Credentials
import numpy as np

# -----------------------------------------------------------------
# KONFIGURASI HALAMAN - LEBIH KOMPAK
# -----------------------------------------------------------------
st.set_page_config(
    page_title="AlphaStock", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="collapsed"  # Sidebar collapsed by default
)

# -----------------------------------------------------------------
# CUSTOM CSS - PREMIUM DARK THEME
# -----------------------------------------------------------------
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0B1120 0%, #1A1F35 100%);
    }
    
    /* Header lebih kompak */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 100% !important;
    }
    
    /* Tabs styling - lebih rapat */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(15, 23, 42, 0.6);
        padding: 4px;
        border-radius: 12px;
        margin-bottom: 15px;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 6px 12px !important;
        color: #94A3B8;
        font-weight: 500;
        font-size: 0.85rem !important;
        white-space: nowrap;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3B82F6, #8B5CF6) !important;
        color: white !important;
    }
    
    /* Metric cards lebih kompak */
    div[data-testid="metric-container"] {
        background: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        padding: 12px !important;
        backdrop-filter: blur(8px);
    }
    
    div[data-testid="metric-container"] label {
        color: #94A3B8 !important;
        font-size: 0.75rem !important;
    }
    
    div[data-testid="metric-container"] div {
        color: #F0F9FF !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
    }
    
    /* Input fields lebih kecil */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        background: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
    }
    
    input, select, textarea {
        color: #F0F9FF !important;
        font-size: 0.9rem !important;
        padding: 8px 12px !important;
    }
    
    .stTextInput label, .stSelectbox label, .stDateInput label, .stNumberInput label {
        color: #94A3B8 !important;
        font-size: 0.8rem !important;
        margin-bottom: 2px !important;
    }
    
    /* Form horizontal untuk entry */
    .horizontal-form {
        display: flex;
        flex-direction: row;
        gap: 10px;
        align-items: flex-end;
        background: rgba(15, 23, 42, 0.4);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
        flex-wrap: wrap;
    }
    
    .form-item {
        flex: 1;
        min-width: 120px;
    }
    
    /* Button lebih kecil */
    .stButton>button {
        background: linear-gradient(135deg, #3B82F6, #8B5CF6);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 6px 16px !important;
        font-size: 0.85rem !important;
        font-weight: 500;
        height: auto !important;
    }
    
    /* Table styling dengan color scale */
    .stDataFrame {
        background: rgba(15, 23, 42, 0.4);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .stDataFrame table {
        border-collapse: separate;
        border-spacing: 0;
        width: 100%;
        font-size: 0.85rem !important;
    }
    
    .stDataFrame th {
        background: rgba(59, 130, 246, 0.2) !important;
        color: #F0F9FF !important;
        font-weight: 600 !important;
        font-size: 0.75rem !important;
        padding: 8px !important;
        border-bottom: 1px solid rgba(59, 130, 246, 0.3) !important;
    }
    
    .stDataFrame td {
        color: #CBD5E1 !important;
        padding: 6px 8px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.03) !important;
    }
    
    /* Hover effect */
    .stDataFrame tr:hover td {
        background: rgba(59, 130, 246, 0.1) !important;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .stTabs [data-baseweb="tab"] {
            padding: 4px 8px !important;
            font-size: 0.75rem !important;
        }
        
        div[data-testid="metric-container"] div {
            font-size: 1rem !important;
        }
        
        .stDataFrame {
            overflow-x: auto;
        }
        
        .stDataFrame table {
            min-width: 800px;
        }
    }
    
    /* Color scale untuk kolom P&L dan Change % akan di-handle oleh JavaScript */
    </style>
    
    <script>
    // Color scale untuk tabel
    function colorTable() {
        const tables = document.querySelectorAll('.stDataFrame table');
        tables.forEach(table => {
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                
                // P&L column (index 11)
                if (cells.length >= 12) {
                    const pnlCell = cells[11];
                    const pnlText = pnlCell?.textContent || '';
                    const pnlValue = parseFloat(pnlText.replace(/[^0-9-]/g, ''));
                    
                    if (!isNaN(pnlValue)) {
                        if (pnlValue > 0) {
                            pnlCell.style.background = 'linear-gradient(90deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.05))';
                            pnlCell.style.color = '#A7F3D0';
                            pnlCell.style.fontWeight = '600';
                        } else if (pnlValue < 0) {
                            pnlCell.style.background = 'linear-gradient(90deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.05))';
                            pnlCell.style.color = '#FECACA';
                            pnlCell.style.fontWeight = '600';
                        }
                    }
                }
                
                // Change % column (index 10)
                if (cells.length >= 11) {
                    const changeCell = cells[10];
                    const changeText = changeCell?.textContent || '';
                    const changeValue = parseFloat(changeText.replace(/[^0-9.-]/g, ''));
                    
                    if (!isNaN(changeValue)) {
                        if (changeValue > 0) {
                            changeCell.style.background = 'linear-gradient(90deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.02))';
                            changeCell.style.color = '#A7F3D0';
                            changeCell.style.fontWeight = '500';
                        } else if (changeValue < 0) {
                            changeCell.style.background = 'linear-gradient(90deg, rgba(239, 68, 68, 0.15), rgba(239, 68, 68, 0.02))';
                            changeCell.style.color = '#FECACA';
                            changeCell.style.fontWeight = '500';
                        }
                    }
                }
            });
        });
    }
    
    // Run on load and after any update
    document.addEventListener('DOMContentLoaded', colorTable);
    setTimeout(colorTable, 1000);
    </script>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------
# HEADER KOMPAK
# -----------------------------------------------------------------
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    st.markdown("### 📊")
with col2:
    st.markdown("### AlphaStock")
with col3:
    st.markdown(f"*{datetime.now().strftime('%d/%m/%Y')}*")

st.divider()

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
        
        # Filter empty rows
        df = df[df['Stock Code'].astype(str).str.strip() != '']
        
        # Clean numeric columns
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
        
        # Convert date columns
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
# TABS
# =========================================================================
tabs = st.tabs(["📊", "➕", "✏️", "📈", "🗑️"])

# ==========================================
# TAB 1: DASHBOARD
# ==========================================
with tabs[0]:
    if not df.empty:
        # Metrics ringkas
        df_open = df[df['Position'].str.contains('Open|Floating', case=False, na=False)]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Value", f"Rp {df_open['Value (Buy)'].sum():,.0f}")
        with col2:
            pnl = df_open['P&L'].sum()
            st.metric("P&L", f"Rp {pnl:,.0f}", delta=f"{pnl/df_open['Value (Buy)'].sum()*100:.1f}%" if df_open['Value (Buy)'].sum() > 0 else "0%")
        with col3:
            win_rate = (df_open[df_open['P&L'] > 0].shape[0] / df_open.shape[0] * 100) if not df_open.empty else 0
            st.metric("Win Rate", f"{win_rate:.1f}%")
        with col4:
            st.metric("Total Lot", f"{df_open['Qty Lot'].sum():.0f}")
        
        st.divider()
        
        # Transaction Table dengan color scale
        st.markdown("### 📋 Transactions")
        
        # Format untuk display
        display_cols = ['Buy Date', 'Stock Code', 'Qty Lot', 'Price (Buy)', 'Position', 'Change %', 'P&L']
        df_display = df[display_cols].copy()
        
        # Format dates
        df_display['Buy Date'] = df_display['Buy Date'].dt.strftime('%d/%m/%y')
        
        # Round numbers
        df_display['Change %'] = df_display['Change %'].round(1)
        df_display['P&L'] = df_display['P&L'].round(0)
        
        st.dataframe(
            df_display,
            use_container_width=True,
            column_config={
                "Buy Date": "Date",
                "Stock Code": "Stock",
                "Qty Lot": "Lot",
                "Price (Buy)": st.column_config.NumberColumn("Buy Price", format="Rp %d"),
                "Position": "Pos",
                "Change %": st.column_config.NumberColumn("Chg %", format="%.1f %%"),
                "P&L": st.column_config.NumberColumn("P&L", format="Rp %d"),
            },
            hide_index=True,
            height=300
        )
        
    else:
        st.info("Belum ada data. Tambah di tab ➕")

# ==========================================
# TAB 2: ADD - HORIZONTAL FORM
# ==========================================
with tabs[1]:
    st.markdown("### ➕ Add Transaction")
    
    # Horizontal form
    with st.form("add_form", clear_on_submit=True):
        cols = st.columns([1.2, 1, 0.8, 1, 1, 0.8])
        
        with cols[0]:
            buy_date = st.date_input("Date", date.today(), label_visibility="collapsed", placeholder="Date")
        with cols[1]:
            stock = st.text_input("Stock", "", placeholder="BBCA", label_visibility="collapsed").upper()
        with cols[2]:
            lot = st.number_input("Lot", 1, step=1, label_visibility="collapsed", placeholder="Lot")
        with cols[3]:
            price = st.number_input("Price", 1, step=10, label_visibility="collapsed", placeholder="Price")
        with cols[4]:
            pos = st.selectbox("Pos", ["Open", "Closed"], label_visibility="collapsed")
        with cols[5]:
            submitted = st.form_submit_button("➕", use_container_width=True)
        
        if submitted:
            if not stock:
                st.error("Stock code required!")
            else:
                try:
                    new_row = [
                        buy_date.strftime("%Y-%m-%d"),
                        stock,
                        lot,
                        price,
                        "", "", "", "", "",
                        "Open/Floating" if pos == "Open" else "Closed",
                        "", "", "", ""
                    ]
                    worksheet.append_row(new_row, value_input_option='USER_ENTERED')
                    st.cache_data.clear()
                    st.success(f"✅ {stock} added")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# ==========================================
# TAB 3: UPDATE
# ==========================================
with tabs[2]:
    st.markdown("### ✏️ Update Position")
    
    if not df.empty:
        # Simple select
        options = [f"{row['Stock Code']} - {row['Buy Date'].strftime('%d/%m')}" for _, row in df.iterrows()]
        selected = st.selectbox("Select", options)
        
        if selected:
            idx = options.index(selected)
            row = df.iloc[idx]
            gsheet_row = idx + 2
            
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                new_pos = st.selectbox("Position", ["Open/Floating", "Closed"], 
                                      index=0 if 'Open' in row['Position'] else 1)
            with col2:
                custom_date = st.date_input("Custom Date", date.today())
            with col3:
                if st.button("Update", use_container_width=True):
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
                        st.error(f"Error: {str(e)}")
    else:
        st.info("No data")

# ==========================================
# TAB 4: ANALYTICS
# ==========================================
with tabs[3]:
    st.markdown("### 📈 Analytics")
    
    if not df.empty and not df[df['Position'].str.contains('Open', na=False)].empty:
        df_open = df[df['Position'].str.contains('Open', na=False)]
        
        # Simple charts
        col1, col2 = st.columns(2)
        
        with col1:
            # P&L by Stock
            fig = go.Figure()
            colors = ['#10B981' if x > 0 else '#EF4444' for x in df_open['P&L']]
            fig.add_trace(go.Bar(
                x=df_open['Stock Code'],
                y=df_open['P&L'],
                marker_color=colors
            ))
            fig.update_layout(
                title="P&L by Stock",
                template="plotly_dark",
                height=250,
                margin=dict(l=20, r=20, t=40, b=20),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Win/Loss Pie
            wins = (df_open['P&L'] > 0).sum()
            losses = (df_open['P&L'] < 0).sum()
            
            fig = go.Figure(data=[go.Pie(
                labels=['Win', 'Loss'],
                values=[wins, losses],
                marker_colors=['#10B981', '#EF4444']
            )])
            fig.update_layout(
                title="Win/Loss Ratio",
                template="plotly_dark",
                height=250,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No active positions")

# ==========================================
# TAB 5: DELETE
# ==========================================
with tabs[4]:
    st.markdown("### 🗑️ Delete")
    
    if not df.empty:
        options = [f"{row['Stock Code']} - {row['Buy Date'].strftime('%d/%m/%y')}" for _, row in df.iterrows()]
        to_delete = st.selectbox("Select to delete", options)
        
        if to_delete:
            idx = options.index(to_delete)
            row = df.iloc[idx]
            gsheet_row = idx + 2
            
            st.warning(f"Delete {row['Stock Code']}?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Confirm", use_container_width=True):
                    try:
                        worksheet.delete_rows(gsheet_row)
                        st.cache_data.clear()
                        st.success("✅ Deleted")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            with col2:
                if st.button("Cancel", use_container_width=True):
                    st.rerun()
    else:
        st.info("No data")

# -----------------------------------------------------------------
# FOOTER
# -----------------------------------------------------------------
st.divider()
st.caption(f"AlphaStock • {len(df) if not df.empty else 0} transactions • Last: {datetime.now().strftime('%H:%M')}")
