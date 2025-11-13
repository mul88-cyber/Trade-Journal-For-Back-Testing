import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests
import numpy as np

# ==============================================================================
# ⚙️ 1. KONFIGURASI APLIKASI
# ==============================================================================
st.set_page_config(
    page_title="Trading Journal Pro",
    page_icon="📈",
    layout="wide"
)

# ==============================================================================
# 🔐 2. KONEKSI GOOGLE SHEET & API
# ==============================================================================

# [IMPROVEMENT 1] Menggunakan st.secrets["gsheet"]["key"] agar lebih "proper"
@st.cache_resource(ttl=600)
def setup_gsheet():
    """Otentikasi ke Google Sheets menggunakan st.secrets."""
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    
    try:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=scope
        )
        client = gspread.authorize(creds)
        
        # Ambil sheet key dari secrets
        if "gsheet" not in st.secrets or "key" not in st.secrets["gsheet"]:
            st.error("Missing GSheet Key in st.secrets. Add [gsheet] section with 'key = \"...\"' to secrets.toml")
            return None, None
            
        sheet = client.open_by_key(st.secrets["gsheet"]["key"]).sheet1
        headers = sheet.row_values(1) # Ambil header untuk update
        return sheet, headers
    except Exception as e:
        st.error(f"Gagal koneksi ke Google Sheets: {e}")
        return None, None

@st.cache_data(ttl=60)
def get_current_price(symbol):
    """Ambil harga saat ini dari Bybit API (v2)."""
    try:
        url = f"https://api.bybit.com/v2/public/tickers?symbol={symbol}"
        response = requests.get(url, timeout=3)
        data = response.json()
        if data['ret_code'] == 0 and data['result']:
            return float(data['result'][0]['last_price'])
    except Exception as e:
        # st.toast(f"Gagal ambil harga {symbol}: {e}", icon="⚠️")
        return None
    return None

# ==============================================================================
# 🧮 3. FUNGSI KALKULASI & HELPER
# ==============================================================================

def calculate_pnl(row, current_prices):
    """Menghitung PnL real-time untuk open trades."""
    try:
        # Jika trade sudah ditutup, PnL-nya final
        if pd.notna(row.get('exit_price')) and row.get('exit_price') > 0:
            return row.get('pnl', 0)

        # Jika trade masih open, hitung PnL live
        current_price = current_prices.get(row['pair'])
        if current_price and pd.notna(row['entry_price']) and row['entry_price'] > 0 and pd.notna(row['position_size']) and row['position_size'] > 0:
            
            # [IMPROVEMENT 2] Perhitungan PnL yang "proper" untuk Linear Contract
            # Quantity (Coin) = Position Size (USDT) / Entry Price
            quantity = row['position_size'] / row['entry_price']
            
            if row['direction'] == 'LONG':
                pnl = (current_price - row['entry_price']) * quantity
            else: # SHORT
                pnl = (row['entry_price'] - current_price) * quantity
            return pnl
    except Exception:
        pass # Tangkap jika ada data buruk
    return 0 # Default PnL 0 jika ada error

def calculate_final_pnl_percent(entry, exit_p, pos_size, leverage, direction):
    """Menghitung PnL dan PnL % final saat trade ditutup."""
    if not all([entry > 0, exit_p > 0, pos_size > 0, leverage > 0]):
        return 0, 0
    
    quantity = pos_size / entry
    
    if direction == 'LONG':
        pnl = (exit_p - entry) * quantity
    else: # SHORT
        pnl = (entry - exit_p) * quantity
        
    margin = pos_size / leverage
    pnl_percent = (pnl / margin) * 100
    
    return pnl, pnl_percent

def calculate_rr(entry, sl, tp):
    """Menghitung Risk:Reward Ratio."""
    try:
        if (entry - sl) == 0: return 0
        rr = abs(tp - entry) / abs(entry - sl)
        return rr
    except Exception:
        return 0

# ==============================================================================
# 📈 4. UTAMA: JUDUL & LOAD DATA
# ==============================================================================
st.title("📈 Trading Journal Pro")
st.caption("Analisis performa Anda untuk trading yang lebih disiplin dan profitabel.")

sheet, headers = setup_gsheet()

# Load data
df = pd.DataFrame()
if sheet:
    try:
        records = sheet.get_all_records(empty_value=np.nan, head=1) # Gunakan head=1
        df = pd.DataFrame(records)
        df['gsheet_row'] = df.index + 2 # Simpan GSheet row index (PENTING untuk update)

        if not df.empty:
            # Konversi kolom numerik
            numeric_cols = ['entry_price', 'stop_loss', 'take_profit', 'exit_price', 
                            'position_size', 'pnl', 'pnl_percent', 'risk_reward_ratio', 'leverage']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0) # Ganti NaN/blank dgn 0
            
            # Konversi kolom tanggal
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            
            # Ambil harga saat ini untuk PnL live
            current_prices = {}
            open_pairs = df.loc[df['exit_price'] == 0, 'pair'].unique()
            for pair in open_pairs:
                if pair:
                    current_prices[pair] = get_current_price(pair)
            
            # Hitung PnL (live untuk open, final untuk closed)
            df['current_pnl'] = df.apply(calculate_pnl, axis=1, args=(current_prices,))
            
        else:
            st.info("No trades recorded yet. Start by adding your first trade! 🚀")

    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()
else:
    st.error("Koneksi Google Sheet gagal. Cek `st.secrets` Anda.")
    st.stop()


# ==============================================================================
# 📝 5. SIDEBAR: INPUT TRADE BARU
# ==============================================================================
st.sidebar.header("➕ Input Trade Baru")

with st.sidebar.form("trade_entry", clear_on_submit=True):
    st.markdown("**Detail Eksekusi**")
    timestamp = st.date_input("Trade Date", datetime.now())
    pair = st.selectbox("Pair", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "XRPUSDT", "DOGEUSDT", "PEPEUSDT"])
    direction = st.radio("Direction", ["LONG", "SHORT"])
    
    col1, col2 = st.columns(2)
    with col1:
        entry_price = st.number_input("Entry Price", min_value=0.0, format="%.4f")
        position_size = st.number_input("Position Size (USDT)", min_value=1.0)
        leverage = st.number_input("Leverage", min_value=1, value=10)
    with col2:
        stop_loss = st.number_input("Stop Loss", min_value=0.0, format="%.4f")
        take_profit = st.number_input("Take Profit", min_value=0.0, format="%.4f")
    
    st.markdown("**Detail Analisis**")
    # [IMPROVEMENT 2] Menambahkan input Strategy, Timeframe, Tags
    strategy = st.selectbox("Strategy", ["Breakout", "Continuation", "Mean Reversion", "Scalp", "News", "Other"])
    timeframe = st.selectbox("Timeframe", ["1m", "5m", "15m", "1H", "4H", "1D"])
    setup_quality = st.selectbox("Setup Quality", ["A (High Prob)", "B (Good)", "C (FOMO)"])
    emotion_pre = st.selectbox("Pre-Trade Emotion", ["Confident", "Calm", "Anxious", "Greedy", "Fearful", "Bored"])
    tags = st.multiselect("Tags", ["News-driven", "High-RSI", "Divergence", "Support-Bounce", "Resist-Reject", "FOMO-Entry"])
    
    notes = st.text_area("Trade Notes / Setup Description")
    
    if st.form_submit_button("💾 Save Trade"):
        if entry_price == 0 or position_size == 0 or stop_loss == 0 or take_profit == 0:
            st.sidebar.error("Entry, Size, SL, dan TP tidak boleh 0.")
        else:
            # Hitung R:R
            rr = calculate_rr(entry_price, stop_loss, take_profit)
            
            # Buat list data baru sesuai urutan header GSheet
            new_trade_data = [
                timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                pair,
                direction,
                entry_price,
                stop_loss,
                take_profit,
                position_size,
                leverage,
                setup_quality,
                emotion_pre,
                notes, # lesson_learned
                np.nan, # exit_price (kosong)
                np.nan, # pnl (kosong)
                np.nan, # pnl_percent (kosong)
                rr,
                "", # emotion_post_trade (kosong)
                strategy,
                timeframe,
                ", ".join(tags) # Gabung tags
            ]
            
            try:
                sheet.append_row(new_trade_data, value_input_option='USER_ENTERED')
                st.sidebar.success("Trade saved successfully! 🎯")
                st.rerun() # Refresh data
            except Exception as e:
                st.sidebar.error(f"Error saving trade: {e}")

# ==============================================================================
# 📊 6. MAIN DASHBOARD (DENGAN TABS)
# ==============================================================================
if not df.empty:
    
    # Pisahkan trade open dan closed
    closed_trades = df[df['exit_price'] > 0].copy()
    open_trades = df[df['exit_price'] == 0].copy()

    # [IMPROVEMENT 5] Menggunakan Tabs untuk UI yang lebih rapi
    tab_overview, tab_analytics, tab_history = st.tabs([
        f"📊 Overview ({len(open_trades)} Open)", 
        "🔬 Analytics", 
        "📋 Trade History"
    ])

    # --- TAB 1: OVERVIEW ---
    with tab_overview:
        st.header("📊 Live Portfolio Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Hitung metrics
        total_trades = len(df)
        total_closed_trades = len(closed_trades)
        winning_trades = len(closed_trades[closed_trades['pnl'] > 0])
        win_rate = (winning_trades / total_closed_trades * 100) if total_closed_trades > 0 else 0
        
        total_pnl = closed_trades['pnl'].sum()
        open_pnl = open_trades['current_pnl'].sum()
        
        avg_rr = closed_trades['risk_reward_ratio'].mean()
        avg_win = closed_trades[closed_trades['pnl'] > 0]['pnl'].mean()
        avg_loss = closed_trades[closed_trades['pnl'] < 0]['pnl'].mean()
        profit_factor = abs(closed_trades[closed_trades['pnl'] > 0]['pnl'].sum() / closed_trades[closed_trades['pnl'] < 0]['pnl'].sum()) if closed_trades[closed_trades['pnl'] < 0]['pnl'].sum() != 0 else 0
        
        with col1:
            st.metric("Total Trades", total_trades)
            st.metric("Win Rate", f"{win_rate:.1f}%")
        with col2:
            st.metric("Avg. R:R", f"{avg_rr:.2f}R")
            st.metric("Profit Factor", f"{profit_factor:.2f}")
        with col3:
            st.metric("Avg. Win", f"${avg_win:,.2f}")
            st.metric("Avg. Loss", f"${avg_loss:,.2f}")
        with col4:
            st.metric("Closed PnL", f"${total_pnl:,.2f}")
            st.metric("Open PnL", f"${open_pnl:,.2f}", delta=f"{open_pnl:,.2f}")

        st.markdown("---")
        
        # Equity Curve
        st.subheader("Equity Curve (Closed Trades)")
        if not closed_trades.empty:
            closed_trades_sorted = closed_trades.sort_values('timestamp')
            closed_trades_sorted['cumulative_pnl'] = closed_trades_sorted['pnl'].cumsum()
            
            fig = px.line(closed_trades_sorted, x='timestamp', y='cumulative_pnl',
                          title="Cumulative PnL Over Time", labels={'timestamp': 'Date', 'cumulative_pnl': 'Cumulative PnL (USDT)'})
            fig.update_traces(hovertemplate='Date: %{x}<br>PnL: %{y:,.2f}')
            st.plotly_chart(fig, use_container_width=True)

    # --- TAB 2: ANALYTICS ---
    with tab_analytics:
        st.header("🔬 Analytics Dashboard")
        st.caption("Pelajari pola trading Anda untuk menemukan 'edge'.")
        
        if closed_trades.empty:
            st.info("No closed trades to analyze yet.")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                # [IMPROVEMENT 4] Chart PnL by Strategy
                if 'strategy' in closed_trades.columns:
                    strategy_pnl = closed_trades.groupby('strategy')['pnl'].sum().sort_values(ascending=False)
                    fig = px.bar(strategy_pnl, title="Total PnL by Strategy", text_auto='.2s')
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                
                # PnL by Setup Quality
                if 'setup_quality' in closed_trades.columns:
                    quality_pnl = closed_trades.groupby('setup_quality')['pnl'].mean().sort_values(ascending=False)
                    fig = px.bar(quality_pnl, title="Average PnL by Setup Quality", text_auto='.2s')
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                # [IMPROVEMENT 4] Chart PnL by Pre-Trade Emotion
                if 'emotion_pre_trade' in closed_trades.columns:
                    emotion_pnl = closed_trades.groupby('emotion_pre_trade')['pnl'].mean().sort_values(ascending=False)
                    fig = px.bar(emotion_pnl, title="Average PnL by Pre-Trade Emotion", text_auto='.2s')
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                    
                # [IMPROVEMENT 4] PnL Distribution (Histogram)
                fig_hist = px.histogram(closed_trades, x="pnl", nbins=50, title="PnL Distribution (Wins vs Losses)")
                fig_hist.add_vline(x=0, line_dash="dash", line_color="red")
                st.plotly_chart(fig_hist, use_container_width=True)

    # --- TAB 3: TRADE HISTORY ---
    with tab_history:
        
        # [IMPROVEMENT 3] Fitur "Close Trade" menggunakan st.data_editor
        st.header("📋 Trade History")
        
        # Logika Update Google Sheet
        if "edits" in st.session_state:
            if st.button("💾 Save Changes to Google Sheet"):
                with st.spinner("Menyimpan perubahan..."):
                    cells_to_update = []
                    for row_idx, changes in st.session_state["edits"]["edited_rows"].items():
                        # Dapatkan GSheet row number asli
                        gsheet_row_num = open_trades.iloc[row_idx]['gsheet_row']
                        
                        # Ambil data trade untuk kalkulasi
                        trade_row = open_trades.iloc[row_idx]
                        
                        # Siapkan data baru
                        new_exit_price = changes.get('exit_price', trade_row['exit_price'])
                        new_emotion_post = changes.get('emotion_post_trade', trade_row['emotion_post_trade'])
                        new_lesson = changes.get('lesson_learned', trade_row['lesson_learned'])
                        
                        # Jika trade ditutup (exit price diisi)
                        if pd.notna(new_exit_price) and new_exit_price > 0:
                            final_pnl, final_pnl_percent = calculate_final_pnl_percent(
                                trade_row['entry_price'],
                                new_exit_price,
                                trade_row['position_size'],
                                trade_row['leverage'],
                                trade_row['direction']
                            )
                            
                            # Update GSheet
                            try:
                                # Update cell per cell
                                # Note: gspread batch_update lebih efisien, tapi update_cell lebih simpel
                                sheet.update_cell(gsheet_row_num, headers.index('exit_price') + 1, new_exit_price)
                                sheet.update_cell(gsheet_row_num, headers.index('pnl') + 1, final_pnl)
                                sheet.update_cell(gsheet_row_num, headers.index('pnl_percent') + 1, final_pnl_percent)
                                sheet.update_cell(gsheet_row_num, headers.index('emotion_post_trade') + 1, new_emotion_post)
                                sheet.update_cell(gsheet_row_num, headers.index('lesson_learned') + 1, new_lesson)
                            except Exception as e:
                                st.error(f"Gagal update GSheet row {gsheet_row_num}: {e}")

                    st.success("Perubahan berhasil disimpan! Refresh data...")
                    st.cache_data.clear() # Clear cache
                    st.rerun() # Refresh

        # Tampilkan Open Trades dengan data_editor
        if not open_trades.empty:
            st.subheader("🟡 Open Trades (Anda bisa edit di sini untuk menutup trade)")
            open_display_cols = ['timestamp', 'pair', 'direction', 'entry_price', 'position_size', 'leverage', 
                                 'stop_loss', 'take_profit', 'current_pnl', 'setup_quality', 'strategy', 'tags',
                                 'exit_price', 'emotion_post_trade', 'lesson_learned']
            
            # Filter kolom yang ada di df
            open_display_cols_exist = [col for col in open_display_cols if col in open_trades.columns]
            
            st.data_editor(
                open_trades[open_display_cols_exist],
                use_container_width=True,
                key="edits", # Key untuk session state
                column_config={
                    # Non-editable columns
                    "timestamp": st.column_config.DatetimeColumn("Timestamp", disabled=True),
                    "pair": st.column_config.TextColumn("Pair", disabled=True),
                    "direction": st.column_config.TextColumn("Direction", disabled=True),
                    "entry_price": st.column_config.NumberColumn("Entry", format="%.4f", disabled=True),
                    "position_size": st.column_config.NumberColumn("Size (USDT)", format="%.2f", disabled=True),
                    "leverage": st.column_config.NumberColumn("Lev", disabled=True),
                    "stop_loss": st.column_config.NumberColumn("SL", format="%.4f", disabled=True),
                    "take_profit": st.column_config.NumberColumn("TP", format="%.4f", disabled=True),
                    "current_pnl": st.column_config.NumberColumn("Live PnL", format="%.2f", disabled=True),
                    "setup_quality": st.column_config.TextColumn("Setup", disabled=True),
                    "strategy": st.column_config.TextColumn("Strategy", disabled=True),
                    "tags": st.column_config.TextColumn("Tags", disabled=True),
                    
                    # Editable columns
                    "exit_price": st.column_config.NumberColumn("Exit Price", min_value=0.0, format="%.4f", required=False),
                    "emotion_post_trade": st.column_config.SelectboxColumn("Post-Emotion", options=["Puas", "Netral", "Kesal", "Revenge", "Serakah", "Takut"]),
                    "lesson_learned": st.column_config.TextColumn("Lesson / Notes")
                },
                hide_index=True
            )
        
        # Tampilkan Closed Trades (sebagai dataframe biasa)
        if not closed_trades.empty:
            st.subheader("🟢 Closed Trades")
            closed_display_cols = ['timestamp', 'pair', 'direction', 'strategy', 'setup_quality', 'entry_price',
                                   'exit_price', 'position_size', 'pnl', 'pnl_percent', 'risk_reward_ratio', 'emotion_pre_trade', 'emotion_post_trade']
            
            # Filter kolom yang ada di df
            closed_display_cols_exist = [col for col in closed_display_cols if col in closed_trades.columns]
            
            st.dataframe(
                closed_trades[closed_display_cols_exist].sort_values('timestamp', ascending=False), 
                use_container_width=True,
                column_config={
                    "timestamp": st.column_config.DatetimeColumn("Timestamp", format="YYYY-MM-DD"),
                    "pnl": st.column_config.NumberColumn("PnL $", format="%.2f"),
                    "pnl_percent": st.column_config.NumberColumn("PnL %", format="%.2f%%"),
                    "risk_reward_ratio": st.column_config.NumberColumn("R:R", format="%.2f"),
                },
                hide_index=True
            )

# Footer
st.markdown("---")
st.markdown("**Trading Journal Pro** - Built for disciplined traders 🎯")
