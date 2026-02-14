import streamlit as st
import gspread
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
from google.oauth2.service_account import Credentials
import numpy as np

# -----------------------------------------------------------------
# KONFIGURASI HALAMAN & UI CUSTOM (PREMIUM DARK THEME)
# -----------------------------------------------------------------
st.set_page_config(
    page_title="AlphaStock Professional", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Custom CSS dengan efek glassmorphism
st.markdown("""
    <style>
    /* Main background with gradient */
    .stApp {
        background: linear-gradient(135deg, #0B0F1C 0%, #1A1F2F 50%, #0F172A 100%);
        color: #E2E8F0;
    }
    
    /* Glassmorphism cards */
    .css-1r6slb0, .css-12w0qpk, .element-container {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 20px;
    }
    
    /* Premium typography */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        background: linear-gradient(135deg, #60A5FA 0%, #A78BFA 50%, #F472B6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
    }
    
    h1 {
        font-size: 3.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Metric cards */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(96, 165, 250, 0.1), rgba(167, 139, 250, 0.1));
        border: 1px solid rgba(96, 165, 250, 0.2);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(8px);
        transition: transform 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        border-color: rgba(96, 165, 250, 0.4);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.03);
        padding: 8px;
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 10px 20px;
        color: #94A3B8;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3B82F6, #8B5CF6) !important;
        color: white !important;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #3B82F6, #8B5CF6);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.2);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(59, 130, 246, 0.3);
    }
    
    /* Input fields */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        transition: all 0.3s ease;
    }
    
    div[data-baseweb="input"]:focus-within {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .element-container {
        animation: fadeIn 0.5s ease-out;
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
