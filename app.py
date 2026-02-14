import streamlit as st
import gspread
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
from google.oauth2.service_account import Credentials
import numpy as np

# -----------------------------------------------------------------
# KONFIGURASI HALAMAN & UI CUSTOM (LIGHT PROFESSIONAL THEME)
# -----------------------------------------------------------------
st.set_page_config(
    page_title="AlphaStock Professional", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Custom CSS dengan tema Light/Professional
st.markdown("""
    <style>
    /* Main background dengan warna terang */
    .stApp {
        background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 50%, #FFFFFF 100%);
        color: #0F172A;
    }
    
    /* Glassmorphism cards dengan efek transparan light */
    div[data-testid="stVerticalBlock"] > div {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 0, 0, 0.05);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.02);
    }
    
    /* Main container */
    .main > div {
        background: transparent;
    }
    
    /* Block container */
    .st-emotion-cache-1r6slb0, .st-emotion-cache-12w0qpk {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
    }
    
    /* Premium typography - gradient untuk headings */
    h1, h2, h3 {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 0.5rem !important;
    }
    
    h1 {
        font-size: 2.5rem !important;
        background: linear-gradient(135deg, #2563EB 0%, #7C3AED 50%, #DB2777 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    h2 {
        font-size: 2rem !important;
        background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    h3 {
        font-size: 1.5rem !important;
        color: #1E293B !important;
        background: none;
        -webkit-text-fill-color: #1E293B;
    }
    
    /* Regular text */
    p, li, .stMarkdown, .stText, span:not([class*="css"]) {
        color: #334155 !important;
    }
    
    /* Metric cards premium */
    div[data-testid="metric-container"] {
        background: white !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.01);
        transition: all 0.2s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.01);
        border-color: #94A3B8 !important;
    }
    
    /* Metric label */
    div[data-testid="metric-container"] label {
        color: #64748B !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    
    /* Metric value */
    div[data-testid="metric-container"] div {
        color: #0F172A !important;
        font-size: 1.875rem !important;
        font-weight: 700 !important;
        line-height: 1.2 !important;
    }
    
    /* Metric delta */
    div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
        color: #10B981 !important;
        font-size: 0.875rem !important;
    }
    
    /* Tabs styling premium */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: white;
        padding: 6px;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
        margin-bottom: 24px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px;
        padding: 8px 16px;
        color: #64748B;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563EB, #7C3AED) !important;
        color: white !important;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
    }
    
    /* Button styling premium */
    .stButton>button {
        background: linear-gradient(135deg, #2563EB, #7C3AED);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
    }
    
    .stButton>button:active {
        transform: translateY(0);
    }
    
    /* Secondary button */
    .stButton>button[kind="secondary"] {
        background: white;
        color: #2563EB;
        border: 1px solid #E2E8F0;
        box-shadow: none;
    }
    
    .stButton>button[kind="secondary"]:hover {
        background: #F8FAFC;
        border-color: #2563EB;
    }
    
    /* Input fields premium */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"] {
        background: white !important;
        border: 2px solid #E2E8F0 !important;
        border-radius: 12px !important;
        transition: all 0.2s ease;
    }
    
    div[data-baseweb="input"]:hover, div[data-baseweb="select"]:hover {
        border-color: #94A3B8 !important;
    }
    
    div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {
        border-color: #2563EB !important;
        box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1) !important;
    }
    
    /* Input text */
    input, select, textarea {
        color: #0F172A !important;
        font-size: 1rem !important;
        padding: 10px 14px !important;
    }
    
    /* Input label */
    .stTextInput label, .stSelectbox label, .stDateInput label, .stNumberInput label {
        color: #475569 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        margin-bottom: 4px !important;
    }
    
    /* Placeholder */
    input::placeholder, textarea::placeholder {
        color: #94A3B8 !important;
        font-size: 0.95rem !important;
    }
    
    /* Select box */
    .stSelectbox div[data-baseweb="select"] div {
        color: #0F172A !important;
    }
    
    /* Date input */
    .stDateInput div[data-baseweb="input"] {
        background: white !important;
    }
    
    /* Number input */
    .stNumberInput div[data-baseweb="input"] {
        background: white !important;
    }
    
    /* Dataframe styling premium */
    .stDataFrame {
        background: white;
        border-radius: 16px;
        border: 1px solid #E2E8F0;
        overflow: hidden;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
    }
    
    .stDataFrame [data-testid="stDataFrame"] {
        border: none;
    }
    
    /* Table styling */
    .stDataFrame table {
        border-collapse: separate;
        border-spacing: 0;
    }
    
    .stDataFrame th {
        background: #F8FAFC;
        color: #2563EB !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 12px 16px !important;
        border-bottom: 2px solid #E2E8F0 !important;
    }
    
    .stDataFrame td {
        color: #1E293B !important;
        padding: 12px 16px !important;
        border-bottom: 1px solid #F1F5F9 !important;
    }
    
    .stDataFrame tr:hover td {
        background: #F8FAFC !important;
    }
    
    /* Alert/Message styling */
    .stAlert {
        background: white !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 16px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
    }
    
    /* Success message */
    div[data-baseweb="notification"]:has([data-testid="stNotification-success"]) {
        background: #F0FDF4 !important;
        border-color: #86EFAC !important;
    }
    
    .stAlert.success {
        background: #F0FDF4 !important;
        border-left: 4px solid #22C55E !important;
    }
    
    .stAlert.success p {
        color: #166534 !important;
    }
    
    /* Error message */
    .stAlert.error {
        background: #FEF2F2 !important;
        border-left: 4px solid #EF4444 !important;
    }
    
    .stAlert.error p {
        color: #991B1B !important;
    }
    
    /* Warning message */
    .stAlert.warning {
        background: #FFFBEB !important;
        border-left: 4px solid #F59E0B !important;
    }
    
    .stAlert.warning p {
        color: #92400E !important;
    }
    
    /* Info message */
    .stAlert.info {
        background: #EFF6FF !important;
        border-left: 4px solid #3B82F6 !important;
    }
    
    .stAlert.info p {
        color: #1E40AF !important;
    }
    
    /* Sidebar styling premium */
    section[data-testid="stSidebar"] {
        background: white !important;
        border-right: 1px solid #E2E8F0;
        box-shadow: 4px 0 6px -1px rgba(0, 0, 0, 0.02);
    }
    
    section[data-testid="stSidebar"] > div {
        background: white !important;
        padding: 24px 16px;
    }
    
    /* Sidebar text */
    section[data-testid="stSidebar"] .stMarkdown p {
        color: #334155 !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        background: none;
    }
    
    /* Sidebar menu items */
    section[data-testid="stSidebar"] .stButton>button {
        background: transparent;
        color: #475569;
        box-shadow: none;
        border: 1px solid #E2E8F0;
        text-align: left;
        justify-content: flex-start;
    }
    
    section[data-testid="stSidebar"] .stButton>button:hover {
        background: #F8FAFC;
        border-color: #2563EB;
        color: #2563EB;
    }
    
    /* Divider */
    hr {
        border-color: #E2E8F0 !important;
        margin: 24px 0 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: white !important;
        color: #2563EB !important;
        font-weight: 600 !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: #F8FAFC !important;
    }
    
    .streamlit-expanderContent {
        background: white !important;
        border: 1px solid #E2E8F0 !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
        padding: 16px !important;
    }
    
    /* Checkbox */
    .stCheckbox label {
        color: #334155 !important;
    }
    
    .stCheckbox div[data-baseweb="checkbox"] {
        border-color: #94A3B8 !important;
    }
    
    .stCheckbox div[data-baseweb="checkbox"]:checked {
        background: #2563EB !important;
        border-color: #2563EB !important;
    }
    
    /* Radio button */
    .stRadio label {
        color: #334155 !important;
    }
    
    .stRadio div[data-baseweb="radio"] {
        border-color: #94A3B8 !important;
    }
    
    .stRadio div[data-baseweb="radio"]:checked {
        background: #2563EB !important;
        border-color: #2563EB !important;
    }
    
    /* Multiselect */
    .stMultiSelect div[data-baseweb="select"] {
        background: white !important;
        border: 2px solid #E2E8F0 !important;
        border-radius: 12px !important;
    }
    
    .stMultiSelect div[data-baseweb="select"]:hover {
        border-color: #94A3B8 !important;
    }
    
    .stMultiSelect div[data-baseweb="select"]:focus-within {
        border-color: #2563EB !important;
        box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1) !important;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #2563EB, #7C3AED) !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #2563EB transparent #2563EB transparent !important;
    }
    
    /* Caption/small text */
    .stCaption, small, .stSmall, .stMarkdown small {
        color: #64748B !important;
        font-size: 0.8rem !important;
    }
    
    /* Link */
    a {
        color: #2563EB !important;
        text-decoration: none !important;
        font-weight: 500 !important;
    }
    
    a:hover {
        text-decoration: underline !important;
    }
    
    /* Code block */
    code {
        background: #F1F5F9 !important;
        color: #DB2777 !important;
        padding: 2px 6px !important;
        border-radius: 6px !important;
        font-size: 0.9em !important;
    }
    
    /* Tooltip */
    [data-testid="stTooltip"] {
        background: white !important;
        color: #0F172A !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .element-container, div[data-testid="stVerticalBlock"] > div {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Scrollbar styling premium */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #F1F5F9;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #94A3B8;
        border-radius: 5px;
        border: 2px solid #F1F5F9;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #64748B;
    }
    
    /* Loading states */
    .stLoading {
        background: linear-gradient(90deg, transparent, rgba(37, 99, 235, 0.1), transparent);
    }
    
    /* Print styles */
    @media print {
        .stApp {
            background: white !important;
        }
        
        section[data-testid="stSidebar"] {
            display: none !important;
        }
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        h1 {
            font-size: 1.8rem !important;
        }
        
        h2 {
            font-size: 1.5rem !important;
        }
        
        h3 {
            font-size: 1.2rem !important;
        }
        
        div[data-testid="metric-container"] {
            padding: 12px !important;
        }
        
        div[data-testid="metric-container"] div {
            font-size: 1.5rem !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 6px 12px !important;
            font-size: 0.8rem !important;
        }
        
        .stButton>button {
            padding: 8px 16px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------
# SIDEBAR PREMIUM
# -----------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/stock.png", width=80)
    st.markdown("## AlphaStock Pro")
    st.markdown("---")
    
    # Portfolio Summary Card
    st.markdown("### 📊 Ringkasan Portfolio")
    
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with col2:
        if st.button("📊 Export", use_container_width=True):
            st.success("Export feature coming soon!")
    
    st.markdown("---")
    st.markdown("### 📈 Market Overview")
    # Placeholder for market data
    st.info("Market data akan tersedia segera")
    
    st.markdown("---")
    st.caption("© 2024 AlphaStock Professional")

# -----------------------------------------------------------------
# HEADER SECTION
# -----------------------------------------------------------------
col_logo, col_title, col_date = st.columns([1, 2, 1])
with col_logo:
    st.markdown("📊")
with col_title:
    st.markdown("# AlphaStock Professional")
    st.markdown("*Advanced Trading Journal & Portfolio Analytics*")
with col_date:
    st.markdown(f"### {datetime.now().strftime('%d %B %Y')}")
    st.markdown(f"*Last updated: {datetime.now().strftime('%H:%M:%S')}*")

st.divider()

# -----------------------------------------------------------------
# KONEKSI KE GOOGLE SHEETS (dengan error handling yang lebih baik)
# -----------------------------------------------------------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

COLUMNS = [
    "Buy Date", "Stock Code", "Qty Lot", "Price (Buy)", "Value (Buy)", 
    "Current Date", "Current Price", "Custom Date", "Custom Price", 
    "Position", "Change %", "P&L", "Change % (Custom)", "P&L (Custom)",
    "Sector", "Notes"
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
            
        df = pd.DataFrame(data[1:], columns=COLUMNS[:len(data[0])])
        
        # Filter empty rows
        df = df[df['Stock Code'].astype(str).str.strip() != '']
        
        # Smart cleaning function
        def clean_number(x):
            if pd.isna(x) or x == '':
                return 0.0
            if isinstance(x, str):
                x = x.replace('Rp', '').replace('$', '').replace(',', '')
                x = x.replace(' ', '').replace('%', '').strip()
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

# Initialize connection
client = get_gsheet_client()
if client:
    worksheet, df = load_data(client)
else:
    st.stop()

# -----------------------------------------------------------------
# ADVANCED ANALYTICS FUNCTIONS
# -----------------------------------------------------------------
def calculate_portfolio_metrics(df):
    """Calculate comprehensive portfolio metrics"""
    df_open = df[df['Position'].str.contains('Open|Floating', case=False, na=False)]
    
    metrics = {
        'total_value': df_open['Value (Buy)'].sum() if not df_open.empty else 0,
        'total_pnl': df_open['P&L'].sum() if not df_open.empty else 0,
        'total_pnl_custom': df_open['P&L (Custom)'].sum() if not df_open.empty else 0,
        'total_stocks': len(df_open),
        'total_lots': df_open['Qty Lot'].sum() if not df_open.empty else 0,
        'win_rate': (df_open[df_open['P&L'] > 0].shape[0] / df_open.shape[0] * 100) if not df_open.empty else 0,
        'avg_return': df_open['Change %'].mean() if not df_open.empty else 0,
        'best_performer': df_open.loc[df_open['Change %'].idxmax(), 'Stock Code'] if not df_open.empty and not df_open['Change %'].isna().all() else '-',
        'worst_performer': df_open.loc[df_open['Change %'].idxmin(), 'Stock Code'] if not df_open.empty and not df_open['Change %'].isna().all() else '-'
    }
    
    return metrics

def create_performance_chart(df):
    """Create interactive performance chart"""
    if df.empty:
        return go.Figure()
    
    df_chart = df[df['Position'].str.contains('Open|Floating', case=False, na=False)].copy()
    if df_chart.empty:
        return go.Figure()
    
    fig = go.Figure()
    
    # Add bars for P&L
    colors = ['#10B981' if x > 0 else '#EF4444' for x in df_chart['P&L']]
    fig.add_trace(go.Bar(
        x=df_chart['Stock Code'],
        y=df_chart['P&L'],
        name='P&L Real-Time',
        marker_color=colors,
        text=df_chart['P&L'].apply(lambda x: f'Rp {x:,.0f}'),
        textposition='outside',
    ))
    
    fig.update_layout(
        title='Portfolio Performance by Stock',
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis_title='P&L (Rp)',
        xaxis_title='Stock Code',
        showlegend=False,
        height=400
    )
    
    return fig

def create_sector_distribution(df):
    """Create sector distribution pie chart"""
    if df.empty or 'Sector' not in df.columns:
        return go.Figure()
    
    df_sector = df[df['Position'].str.contains('Open|Floating', case=False, na=False)]
    if df_sector.empty:
        return go.Figure()
    
    sector_value = df_sector.groupby('Sector')['Value (Buy)'].sum().reset_index()
    
    fig = px.pie(
        sector_value, 
        values='Value (Buy)', 
        names='Sector',
        title='Portfolio by Sector',
        template='plotly_dark',
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=350
    )
    
    return fig

# =========================================================================
# MAIN CONTENT WITH TABS
# =========================================================================
tab_overview, tab_portfolio, tab_add, tab_update, tab_analytics, tab_del = st.tabs([
    "📊 Overview", "💼 Portfolio", "➕ Entry", "✏️ Update", "📈 Analytics", "🗑️ Delete"
])

# ==========================================
# 1. OVERVIEW DASHBOARD
# ==========================================
with tab_overview:
    st.markdown("## Portfolio Overview")
    
    if st.button("🔄 Refresh Data", key="refresh_overview", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    if not df.empty:
        metrics = calculate_portfolio_metrics(df)
        
        # Premium metrics display
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Value Aktif", 
                f"Rp {metrics['total_value']:,.0f}",
                delta=f"{metrics['total_stocks']} Stocks"
            )
        
        with col2:
            delta_color = "normal" if metrics['total_pnl'] >= 0 else "inverse"
            st.metric(
                "Real-Time P&L", 
                f"Rp {metrics['total_pnl']:,.0f}",
                delta=f"{metrics['total_pnl']/metrics['total_value']*100:.2f}%" if metrics['total_value'] > 0 else "0%",
                delta_color="normal"
            )
        
        with col3:
            st.metric(
                "Win Rate", 
                f"{metrics['win_rate']:.1f}%",
                delta=f"Avg Return: {metrics['avg_return']:.2f}%"
            )
        
        with col4:
            st.metric(
                "Total Lots", 
                f"{metrics['total_lots']:.0f}",
                delta=f"Best: {metrics['best_performer']}"
            )
        
        st.divider()
        
        # Charts row
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            fig_performance = create_performance_chart(df)
            if fig_performance.data:
                st.plotly_chart(fig_performance, use_container_width=True)
            else:
                st.info("No active positions to display")
        
        with col_chart2:
            fig_sector = create_sector_distribution(df)
            if fig_sector.data:
                st.plotly_chart(fig_sector, use_container_width=True)
            else:
                st.info("Add sector data to see distribution")
        
        st.divider()
        
        # Recent transactions
        st.markdown("### Recent Transactions")
        df_recent = df.sort_values('Buy Date', ascending=False).head(10)
        
        # Format dataframe for display
        display_cols = ['Buy Date', 'Stock Code', 'Qty Lot', 'Price (Buy)', 'Position', 'P&L', 'Change %']
        df_display = df_recent[display_cols].copy()
        
        st.dataframe(
            df_display,
            use_container_width=True,
            column_config={
                "Buy Date": st.column_config.DateColumn("Buy Date", format="DD/MM/YYYY"),
                "Price (Buy)": st.column_config.NumberColumn("Price (Buy)", format="Rp %d"),
                "P&L": st.column_config.NumberColumn("P&L", format="Rp %d"),
                "Change %": st.column_config.NumberColumn("Change %", format="%.2f %%"),
            },
            hide_index=True
        )
    else:
        st.info("✨ Start your trading journey by adding your first transaction!")

# ==========================================
# 2. PORTFOLIO DETAILS
# ==========================================
with tab_portfolio:
    st.markdown("## Portfolio Details")
    
    if not df.empty:
        # Filter controls
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            position_filter = st.multiselect(
                "Filter by Position",
                options=df['Position'].unique(),
                default=df['Position'].unique()
            )
        
        with col_filter2:
            if 'Sector' in df.columns:
                sector_filter = st.multiselect(
                    "Filter by Sector",
                    options=df['Sector'].dropna().unique()
                )
        
        with col_filter3:
            sort_by = st.selectbox(
                "Sort by",
                options=['Buy Date', 'Stock Code', 'P&L', 'Change %', 'Value (Buy)']
            )
        
        # Apply filters
        df_filtered = df[df['Position'].isin(position_filter)] if position_filter else df
        
        if 'Sector' in df.columns and sector_filter:
            df_filtered = df_filtered[df_filtered['Sector'].isin(sector_filter)]
        
        # Display full portfolio
        st.markdown(f"### Showing {len(df_filtered)} transactions")
        
        st.dataframe(
            df_filtered.sort_values(sort_by, ascending=False),
            use_container_width=True,
            column_config={
                "Buy Date": st.column_config.DateColumn("Buy Date", format="DD/MM/YYYY"),
                "Current Date": st.column_config.DateColumn("Current Date", format="DD/MM/YYYY"),
                "Custom Date": st.column_config.DateColumn("Custom Date", format="DD/MM/YYYY"),
                "Price (Buy)": st.column_config.NumberColumn("Price (Buy)", format="Rp %d"),
                "Value (Buy)": st.column_config.NumberColumn("Value (Buy)", format="Rp %d"),
                "Current Price": st.column_config.NumberColumn("Current Price", format="Rp %d"),
                "Custom Price": st.column_config.NumberColumn("Custom Price", format="Rp %d"),
                "P&L": st.column_config.NumberColumn("P&L", format="Rp %d"),
                "P&L (Custom)": st.column_config.NumberColumn("P&L (Custom)", format="Rp %d"),
                "Change %": st.column_config.NumberColumn("Change %", format="%.2f %%"),
                "Change % (Custom)": st.column_config.NumberColumn("Change % (Custom)", format="%.2f %%"),
                "Qty Lot": st.column_config.NumberColumn("Qty Lot", format="%d lot"),
            },
            hide_index=True
        )
        
        # Export option
        if st.button("📥 Export to CSV", use_container_width=True):
            csv = df_filtered.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No portfolio data available")

# ==========================================
# 3. ADD NEW TRANSACTION (ENHANCED)
# ==========================================
with tab_add:
    st.markdown("## Add New Transaction")
    
    with st.form("premium_add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Transaction Details**")
            buy_date = st.date_input("Purchase Date", date.today())
            stock_code = st.text_input("Stock Code*", help="e.g., BBCA, BBRI, TLKM").upper()
            lot_size = st.number_input("Quantity (Lots)*", min_value=1, step=1, value=1)
            
        with col2:
            st.markdown("**Price & Position**")
            buy_price = st.number_input("Purchase Price (Rp)*", min_value=1, step=10, value=1000)
            position = st.selectbox(
                "Initial Position*",
                ["Open/Floating", "Closed"],
                help="Open for active positions, Closed for completed trades"
            )
            sector = st.selectbox(
                "Sector (Optional)",
                ["Banking", "Consumer", "Infrastructure", "Property", "Mining", 
                 "Technology", "Healthcare", "Other"]
            )
        
        notes = st.text_area("Notes (Optional)", placeholder="Add any notes about this transaction...")
        
        submitted = st.form_submit_button("💾 Save Transaction", use_container_width=True)
        
        if submitted:
            if not stock_code:
                st.error("❌ Stock code is required!")
            else:
                with st.spinner("Saving to Google Sheets..."):
                    try:
                        new_row = [
                            buy_date.strftime("%Y-%m-%d"),
                            stock_code,
                            lot_size,
                            buy_price,
                            "",  # Value (Buy) - will be auto-calculated by formula
                            "",  # Current Date
                            "",  # Current Price
                            "",  # Custom Date
                            "",  # Custom Price
                            position,
                            "",  # Change %
                            "",  # P&L
                            "",  # Change % (Custom)
                            "",  # P&L (Custom)
                            sector,
                            notes
                        ]
                        worksheet.append_row(new_row, value_input_option='USER_ENTERED')
                        st.cache_data.clear()
                        st.success(f"✅ Transaction for {stock_code} added successfully!")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to save: {str(e)}")

# ==========================================
# 4. UPDATE TRANSACTION (ENHANCED)
# ==========================================
with tab_update:
    st.markdown("## Update Transaction")
    
    if not df.empty:
        # Search functionality
        search_term = st.text_input("🔍 Search by Stock Code", "").upper()
        
        if search_term:
            df_search = df[df['Stock Code'].str.contains(search_term, na=False)]
        else:
            df_search = df
        
        # Create selection with more info
        df_search['Display'] = df_search.apply(
            lambda x: f"{x.name} - {x['Stock Code']} | Buy: {x['Price (Buy)']:,.0f} | {x['Position']} | P&L: {x['P&L']:,.0f}", 
            axis=1
        )
        
        selected = st.selectbox("Select transaction to update:", df_search['Display'].tolist())
        
        if selected:
            idx = int(selected.split(" - ")[0])
            row = df.iloc[idx]
            gsheet_row = idx + 2
            
            with st.form("premium_update_form"):
                st.info(f"**Editing:** {row['Stock Code']} - Purchased on {row['Buy Date'].strftime('%d/%m/%Y')}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Position Update**")
                    current_pos = row.get('Position', 'Open/Floating')
                    pos_index = 0 if 'Open' in str(current_pos) else 1
                    new_position = st.selectbox(
                        "Update Position Status",
                        ["Open/Floating", "Closed"],
                        index=pos_index
                    )
                    
                with col2:
                    st.markdown("**Scenario Analysis**")
                    custom_date = st.date_input(
                        "Scenario Date",
                        value=row['Custom Date'] if pd.notna(row['Custom Date']) else date.today()
                    )
                
                st.markdown("**Additional Updates**")
                col3, col4 = st.columns(2)
                with col3:
                    if 'Sector' in df.columns:
                        current_sector = row.get('Sector', 'Other')
                        sector_options = ["Banking", "Consumer", "Infrastructure", "Property", "Mining", "Technology", "Healthcare", "Other"]
                        sector_index = sector_options.index(current_sector) if current_sector in sector_options else 7
                        new_sector = st.selectbox("Update Sector", sector_options, index=sector_index)
                
                with col4:
                    new_notes = st.text_area("Update Notes", value=row.get('Notes', ''))
                
                if st.form_submit_button("🔄 Update Transaction", use_container_width=True):
                    with st.spinner("Updating..."):
                        try:
                            updates = [
                                {'range': f'J{gsheet_row}', 'values': [[new_position]]},  # Position
                                {'range': f'H{gsheet_row}', 'values': [[custom_date.strftime("%Y-%m-%d")]]},  # Custom Date
                            ]
                            
                            if 'Sector' in df.columns:
                                updates.append({'range': f'O{gsheet_row}', 'values': [[new_sector]]})
                            
                            if 'Notes' in df.columns:
                                updates.append({'range': f'P{gsheet_row}', 'values': [[new_notes]]})
                            
                            worksheet.batch_update(updates, value_input_option='USER_ENTERED')
                            st.cache_data.clear()
                            st.success("✅ Transaction updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Update failed: {str(e)}")
    else:
        st.info("No transactions to update")

# ==========================================
# 5. ADVANCED ANALYTICS
# ==========================================
with tab_analytics:
    st.markdown("## Advanced Portfolio Analytics")
    
    if not df.empty:
        df_open = df[df['Position'].str.contains('Open|Floating', case=False, na=False)]
        
        if not df_open.empty:
            # Performance metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Performance Distribution")
                
                # P&L Distribution
                fig_dist = go.Figure()
                fig_dist.add_trace(go.Histogram(
                    x=df_open['P&L'],
                    nbinsx=20,
                    marker_color='#3B82F6',
                    name='P&L Distribution'
                ))
                fig_dist.update_layout(
                    title='P&L Distribution',
                    xaxis_title='P&L (Rp)',
                    yaxis_title='Frequency',
                    template='plotly_dark',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_dist, use_container_width=True)
            
            with col2:
                st.markdown("### Top Performers")
                top_5 = df_open.nlargest(5, 'P&L')[['Stock Code', 'P&L', 'Change %']]
                bottom_5 = df_open.nsmallest(5, 'P&L')[['Stock Code', 'P&L', 'Change %']]
                
                tab_top, tab_bottom = st.tabs(["🏆 Top 5", "📉 Bottom 5"])
                
                with tab_top:
                    st.dataframe(
                        top_5,
                        column_config={
                            "P&L": st.column_config.NumberColumn(format="Rp %d"),
                            "Change %": st.column_config.NumberColumn(format="%.2f %%")
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                
                with tab_bottom:
                    st.dataframe(
                        bottom_5,
                        column_config={
                            "P&L": st.column_config.NumberColumn(format="Rp %d"),
                            "Change %": st.column_config.NumberColumn(format="%.2f %%")
                        },
                        hide_index=True,
                        use_container_width=True
                    )
            
            st.divider()
            
            # Risk metrics
            st.markdown("### Risk Analysis")
            
            col_risk1, col_risk2, col_risk3, col_risk4 = st.columns(4)
            
            with col_risk1:
                volatility = df_open['Change %'].std() if len(df_open) > 1 else 0
                st.metric("Portfolio Volatility", f"{volatility:.2f}%")
            
            with col_risk2:
                sharpe = (df_open['Change %'].mean() / volatility * np.sqrt(252)) if volatility > 0 else 0
                st.metric("Sharpe Ratio", f"{sharpe:.2f}")
            
            with col_risk3:
                max_loss = df_open['P&L'].min()
                st.metric("Max Loss", f"Rp {max_loss:,.0f}")
            
            with col_risk4:
                max_gain = df_open['P&L'].max()
                st.metric("Max Gain", f"Rp {max_gain:,.0f}")
            
            st.divider()
            
            # Correlation matrix if multiple stocks
            if len(df_open) > 1 and 'Change %' in df_open.columns:
                st.markdown("### Stock Correlation Analysis")
                st.info("Correlation matrix akan tersedia dengan lebih banyak data")
        else:
            st.info("No active positions for analytics")
    else:
        st.info("Add transactions to see analytics")

# ==========================================
# 6. DELETE TRANSACTION (WITH CONFIRMATION)
# ==========================================
with tab_del:
    st.markdown("## Delete Transaction")
    st.warning("⚠️ This action cannot be undone!")
    
    if not df.empty:
        df['Delete_Display'] = df.apply(
            lambda x: f"{x.name} - {x['Stock Code']} | {x['Buy Date'].strftime('%d/%m/%Y')} | {x['Position']}", 
            axis=1
        )
        
        to_delete = st.selectbox("Select transaction to delete:", df['Delete_Display'].tolist())
        
        if to_delete:
            idx_del = int(to_delete.split(" - ")[0])
            row_del = df.iloc[idx_del]
            gsheet_row_del = idx_del + 2
            
            # Show transaction details
            st.markdown("### Transaction to delete:")
            col_del1, col_del2, col_del3 = st.columns(3)
            with col_del1:
                st.write(f"**Stock:** {row_del['Stock Code']}")
            with col_del2:
                st.write(f"**Date:** {row_del['Buy Date'].strftime('%d/%m/%Y')}")
            with col_del3:
                st.write(f"**Value:** Rp {row_del['Value (Buy)']:,.0f}")
            
            # Double confirmation
            confirm1 = st.checkbox("I understand this action cannot be undone")
            confirm2 = st.checkbox(f"Confirm deletion of {row_del['Stock Code']}")
            
            if confirm1 and confirm2:
                if st.button("🗑️ Permanently Delete Transaction", type="primary", use_container_width=True):
                    with st.spinner("Deleting..."):
                        try:
                            worksheet.delete_rows(gsheet_row_del)
                            st.cache_data.clear()
                            st.success("✅ Transaction deleted successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Delete failed: {str(e)}")
    else:
        st.info("No transactions to delete")

# -----------------------------------------------------------------
# FOOTER
# -----------------------------------------------------------------
st.divider()
col_footer1, col_footer2, col_footer3 = st.columns(3)
with col_footer1:
    st.caption(f"Total transactions: {len(df) if not df.empty else 0}")
with col_footer2:
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
with col_footer3:
    st.caption("AlphaStock Pro v2.0")
