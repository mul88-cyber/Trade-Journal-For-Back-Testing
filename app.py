import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

# Page config
st.set_page_config(
    page_title="IDX Trading Journal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium modern look
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    
    /* Cards */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    div[data-testid="stVerticalBlock"] > div:has(div.element-container) {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        margin-bottom: 1.5rem;
    }
    
    /* Headers */
    h1 {
        color: #1a1a2e;
        font-weight: 700;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    h2 {
        color: #16213e;
        font-weight: 600;
        font-size: 1.8rem !important;
        margin-top: 1rem;
    }
    
    h3 {
        color: #0f3460;
        font-weight: 600;
        font-size: 1.4rem !important;
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a2e;
    }
    
    div[data-testid="stMetricDelta"] {
        font-size: 1rem;
        font-weight: 600;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stDateInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    section[data-testid="stSidebar"] > div {
        background: transparent;
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label {
        color: white !important;
    }
    
    /* Dataframe */
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
        border-radius: 10px;
        padding: 1rem;
    }
    
    .stError {
        background-color: #f8d7da;
        border-color: #f5c6cb;
        color: #721c24;
        border-radius: 10px;
        padding: 1rem;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        font-weight: 600;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.5);
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
        color: #1a1a2e;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        h1 {
            font-size: 1.8rem !important;
        }
        h2 {
            font-size: 1.4rem !important;
        }
        div[data-testid="stVerticalBlock"] > div:has(div.element-container) {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize connection to Google Sheets
@st.cache_resource
def init_connection():
    """Initialize connection to Google Sheets"""
    try:
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return None

@st.cache_data(ttl=60)
def load_data(_client):
    """Load data from Google Sheets with caching"""
    try:
        sheet = _client.open_by_key(st.secrets["spreadsheet_id"]).sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        # Convert date columns
        date_columns = ['Buy Date', 'Current Date', 'Custom Date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Convert numeric columns
        numeric_columns = ['Qty Lot', 'Price (Buy)', 'Value (Buy)', 'Current Price', 
                          'Custom Price', 'Change %', 'P&L', 'Change % (Custom)', 'P&L (Custom)']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def add_trade(client, buy_date, stock_code, qty_lot, price_buy):
    """Add new trade to Google Sheets"""
    try:
        sheet = client.open_by_key(st.secrets["spreadsheet_id"]).sheet1
        
        # Format date as string
        buy_date_str = buy_date.strftime('%Y-%m-%d')
        
        # Find the next empty row (skip rows with formulas but no Buy Date)
        all_values = sheet.get_all_values()
        next_row = 2  # Start from row 2 (after header)
        
        for i, row in enumerate(all_values[1:], start=2):  # Skip header
            if not row[0]:  # If Buy Date (column A) is empty
                next_row = i
                break
        else:
            # If all rows have data, append at the end
            next_row = len(all_values) + 1
        
        # Prepare row data
        row = [
            buy_date_str,
            stock_code.upper(),
            qty_lot,
            price_buy,
            "",  # Value (Buy) - will be calculated by formula
            "",  # Current Date - will be calculated by formula
            "",  # Current Price - will be calculated by formula
            "",  # Custom Date
            "",  # Custom Price - will be calculated by formula
            "OPEN",  # Position
            "",  # Change %
            "",  # P&L
            "",  # Change % (Custom)
            ""   # P&L (Custom)
        ]
        
        # Insert at the correct row
        sheet.insert_row(row, next_row)
        
        st.cache_data.clear()  # Clear cache to reload data
        return True
    except Exception as e:
        st.error(f"Error adding trade: {e}")
        return False

def update_trade(client, row_index, column_name, new_value):
    """Update specific cell in Google Sheets"""
    try:
        sheet = client.open_by_key(st.secrets["spreadsheet_id"]).sheet1
        
        # Get header row to find column index
        headers = sheet.row_values(1)
        col_index = headers.index(column_name) + 1
        
        # Update cell (row_index + 2 because: +1 for header, +1 for 0-indexing)
        sheet.update_cell(row_index + 2, col_index, new_value)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error updating trade: {e}")
        return False

def delete_trade(client, row_index):
    """Delete trade from Google Sheets"""
    try:
        sheet = client.open_by_key(st.secrets["spreadsheet_id"]).sheet1
        # Delete row (row_index + 2 because: +1 for header, +1 for 0-indexing)
        sheet.delete_rows(row_index + 2)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error deleting trade: {e}")
        return False

def format_currency(value):
    """Format number as Indonesian Rupiah"""
    if pd.isna(value):
        return "Rp 0"
    return f"Rp {value:,.0f}"

def format_percentage(value):
    """Format number as percentage"""
    if pd.isna(value):
        return "0.00%"
    return f"{value:.2f}%"

# Main App
def main():
    # Header
    st.markdown("# 📈 IDX Trading Journal")
    st.markdown("### Backtesting & Portfolio Management System")
    
    # Initialize connection
    client = init_connection()
    if client is None:
        st.error("⚠️ Failed to connect to Google Sheets. Please check your credentials.")
        return
    
    # Load data
    df = load_data(client)
    
    # Sidebar - Quick Stats Only
    with st.sidebar:
        st.markdown("### 📌 Quick Stats")
        if not df.empty:
            open_positions = len(df[df['Possition'] == 'OPEN'])
            closed_positions = len(df[df['Possition'] == 'CLOSE'])
            st.metric("Open Positions", open_positions)
            st.metric("Closed Positions", closed_positions)
            st.metric("Total Trades", len(df))
        else:
            st.info("No trades yet")
    
    # Main Navigation - Tabs (not in sidebar)
    st.markdown("## 🎯 Navigation")
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard", 
        "➕ Add Trade", 
        "✏️ Update Trade", 
        "🗑️ Delete Trade", 
        "📋 All Trades"
    ])
    
    # Dashboard Tab
    with tab1:
        st.markdown("## Portfolio Overview")
        
        if df.empty:
            st.info("📝 No trades found. Start by adding your first trade!")
            return
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_value_buy = df['Value (Buy)'].sum()
            st.metric("💰 Total Investment", format_currency(total_value_buy))
        
        with col2:
            total_pnl = df['P&L'].sum()
            st.metric("📈 Total P&L", format_currency(total_pnl), 
                     delta=format_percentage(df['Change %'].mean()))
        
        with col3:
            open_trades = len(df[df['Possition'] == 'OPEN'])
            st.metric("🔓 Open Positions", open_trades)
        
        with col4:
            win_rate = len(df[df['P&L'] > 0]) / len(df) * 100 if len(df) > 0 else 0
            st.metric("🎯 Win Rate", f"{win_rate:.1f}%")
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 P&L Distribution")
            fig_pnl = px.bar(
                df.head(10),
                x='Stock Code',
                y='P&L',
                color='P&L',
                color_continuous_scale=['#ff4b4b', '#ffffff', '#00cc66'],
                title="Top 10 Stocks by P&L"
            )
            fig_pnl.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#1a1a2e'),
                showlegend=False
            )
            st.plotly_chart(fig_pnl, use_container_width=True)
        
        with col2:
            st.markdown("### 🥧 Position Status")
            position_counts = df['Possition'].value_counts()
            fig_pie = px.pie(
                values=position_counts.values,
                names=position_counts.index,
                color_discrete_sequence=['#667eea', '#764ba2', '#f093fb']
            )
            fig_pie.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#1a1a2e')
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Recent Trades
        st.markdown("### 📋 Recent Trades")
        recent_df = df.head(10).copy()
        
        # Format display columns
        display_df = recent_df[[
            'Buy Date', 'Stock Code', 'Qty Lot', 'Price (Buy)', 
            'Current Price', 'Change %', 'P&L', 'Possition'
        ]].copy()
        
        # Format numeric columns for display
        display_df['Price (Buy)'] = display_df['Price (Buy)'].apply(lambda x: f"Rp {x:,.0f}" if pd.notna(x) else "-")
        display_df['Current Price'] = display_df['Current Price'].apply(lambda x: f"Rp {x:,.0f}" if pd.notna(x) else "-")
        display_df['Change %'] = display_df['Change %'].apply(format_percentage)
        display_df['P&L'] = display_df['P&L'].apply(format_currency)
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Add Trade Tab
    with tab2:
        st.markdown("## Add New Trade")
        
        with st.form("add_trade_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                buy_date = st.date_input(
                    "📅 Buy Date",
                    value=datetime.now(),
                    max_value=datetime.now()
                )
                
                stock_code = st.text_input(
                    "🏢 Stock Code",
                    placeholder="e.g., BBCA, BMRI, TLKM"
                ).upper()
            
            with col2:
                qty_lot = st.number_input(
                    "📦 Quantity (Lot)",
                    min_value=1,
                    value=1,
                    step=1
                )
                
                price_buy = st.number_input(
                    "💵 Buy Price (per share)",
                    min_value=0.0,
                    value=0.0,
                    step=50.0,
                    format="%.0f"
                )
            
            submitted = st.form_submit_button("✅ Add Trade", use_container_width=True)
            
            if submitted:
                if stock_code and price_buy > 0:
                    if add_trade(client, buy_date, stock_code, qty_lot, price_buy):
                        st.success(f"✅ Trade {stock_code} successfully added!")
                        st.balloons()
                        st.rerun()
                else:
                    st.error("❌ Please fill all required fields!")
    
    # Update Trade Tab
    with tab3:
        st.markdown("## Update Existing Trade")
        
        if df.empty:
            st.info("📝 No trades to update.")
            return
        
        # Select trade to update
        trade_options = [f"{row['Stock Code']} - {row['Buy Date']}" for _, row in df.iterrows()]
        selected_trade = st.selectbox("Select Trade to Update", trade_options)
        
        if selected_trade:
            trade_index = trade_options.index(selected_trade)
            trade = df.iloc[trade_index]
            
            st.markdown(f"### Updating: {trade['Stock Code']}")
            
            # Show current values
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Price", format_currency(trade['Price (Buy)']))
            with col2:
                st.metric("Quantity", f"{trade['Qty Lot']} Lot")
            with col3:
                st.metric("Position", trade['Possition'])
            
            st.markdown("---")
            
            # Update form
            with st.form("update_form"):
                update_type = st.selectbox(
                    "What do you want to update?",
                    ["Position Status", "Custom Date", "Quantity", "Buy Price"]
                )
                
                if update_type == "Position Status":
                    new_position = st.selectbox(
                        "New Position Status",
                        ["OPEN", "CLOSE"],
                        index=0 if trade['Possition'] == 'OPEN' else 1
                    )
                    
                    if st.form_submit_button("💾 Update Position", use_container_width=True):
                        if update_trade(client, trade_index, 'Possition', new_position):
                            st.success("✅ Position updated successfully!")
                            st.rerun()
                
                elif update_type == "Custom Date":
                    custom_date = st.date_input(
                        "Custom Date",
                        value=datetime.now()
                    )
                    
                    if st.form_submit_button("💾 Update Custom Date", use_container_width=True):
                        date_str = custom_date.strftime('%Y-%m-%d')
                        if update_trade(client, trade_index, 'Custom Date', date_str):
                            st.success("✅ Custom date updated successfully!")
                            st.rerun()
                
                elif update_type == "Quantity":
                    new_qty = st.number_input(
                        "New Quantity (Lot)",
                        min_value=1,
                        value=int(trade['Qty Lot']),
                        step=1
                    )
                    
                    if st.form_submit_button("💾 Update Quantity", use_container_width=True):
                        if update_trade(client, trade_index, 'Qty Lot', new_qty):
                            st.success("✅ Quantity updated successfully!")
                            st.rerun()
                
                elif update_type == "Buy Price":
                    new_price = st.number_input(
                        "New Buy Price",
                        min_value=0.0,
                        value=float(trade['Price (Buy)']),
                        step=50.0,
                        format="%.0f"
                    )
                    
                    if st.form_submit_button("💾 Update Price", use_container_width=True):
                        if update_trade(client, trade_index, 'Price (Buy)', new_price):
                            st.success("✅ Price updated successfully!")
                            st.rerun()
    
    # Delete Trade Tab
    with tab4:
        st.markdown("## Delete Trade"))
        
        if df.empty:
            st.info("📝 No trades to delete.")
            return
        
        st.warning("⚠️ Warning: This action cannot be undone!")
        
        # Select trade to delete
        trade_options = [f"{row['Stock Code']} - {row['Buy Date']} - {row['Possition']}" 
                        for _, row in df.iterrows()]
        selected_trade = st.selectbox("Select Trade to Delete", trade_options)
        
        if selected_trade:
            trade_index = trade_options.index(selected_trade)
            trade = df.iloc[trade_index]
            
            # Show trade details
            st.markdown("### Trade Details")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Stock", trade['Stock Code'])
            with col2:
                st.metric("Quantity", f"{trade['Qty Lot']} Lot")
            with col3:
                st.metric("Buy Price", format_currency(trade['Price (Buy)']))
            with col4:
                st.metric("P&L", format_currency(trade['P&L']))
            
            st.markdown("---")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("🗑️ Delete Trade", type="primary", use_container_width=True):
                    if delete_trade(client, trade_index):
                        st.success("✅ Trade deleted successfully!")
                        st.rerun()
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.info("Deletion cancelled.")
    
    # All Trades Tab
    with tab5:
        st.markdown("## All Trades"))
        
        if df.empty:
            st.info("📝 No trades found.")
            return
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            position_filter = st.multiselect(
                "Filter by Position",
                options=['OPEN', 'CLOSE'],
                default=['OPEN', 'CLOSE']
            )
        
        with col2:
            stock_filter = st.multiselect(
                "Filter by Stock",
                options=df['Stock Code'].unique().tolist()
            )
        
        with col3:
            sort_by = st.selectbox(
                "Sort by",
                ['Buy Date', 'P&L', 'Change %', 'Stock Code']
            )
        
        # Apply filters
        filtered_df = df.copy()
        
        if position_filter:
            filtered_df = filtered_df[filtered_df['Possition'].isin(position_filter)]
        
        if stock_filter:
            filtered_df = filtered_df[filtered_df['Stock Code'].isin(stock_filter)]
        
        # Sort
        filtered_df = filtered_df.sort_values(by=sort_by, ascending=False)
        
        # Display
        st.markdown(f"### Showing {len(filtered_df)} trades")
        
        # Format for display
        display_df = filtered_df[[
            'Buy Date', 'Stock Code', 'Qty Lot', 'Price (Buy)', 
            'Current Price', 'Custom Price', 'Change %', 'P&L', 
            'Change % (Custom)', 'P&L (Custom)', 'Possition'
        ]].copy()
        
        display_df['Price (Buy)'] = display_df['Price (Buy)'].apply(lambda x: f"Rp {x:,.0f}" if pd.notna(x) else "-")
        display_df['Current Price'] = display_df['Current Price'].apply(lambda x: f"Rp {x:,.0f}" if pd.notna(x) else "-")
        display_df['Custom Price'] = display_df['Custom Price'].apply(lambda x: f"Rp {x:,.0f}" if pd.notna(x) else "-")
        display_df['Change %'] = display_df['Change %'].apply(format_percentage)
        display_df['P&L'] = display_df['P&L'].apply(format_currency)
        display_df['Change % (Custom)'] = display_df['Change % (Custom)'].apply(format_percentage)
        display_df['P&L (Custom)'] = display_df['P&L (Custom)'].apply(format_currency)
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"idx_trades_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

if __name__ == "__main__":
    main()
