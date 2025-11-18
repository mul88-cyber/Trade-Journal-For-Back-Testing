import streamlit as st
import gspread
import pandas as pd
from datetime import datetime
import numpy as np
import pytz
from google.oauth2.service_account import Credentials

# -----------------------------------------------------------------
# KONEKSI KE GOOGLE SHEETS
# -----------------------------------------------------------------

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# --- Kolom untuk Sheet 'sheet1' (Jurnal Utama) ---
COLUMN_NAMES = [
    "Timestamp", "Pairs", "Direction", "Entry Price", "Stop Loss", 
    "Take Profit", "Exit Price", "Position Size", "PNL (USDT)", "PNL (%)", 
    "RRR", "Leverage", "Timeframe", "Strategy", "Setup Quality", 
    "Emotion Pre-Trade", "Emotion Post-Trade", "Lesson Learned" 
]

# --- Kolom untuk Sheet 'BackTest' (Total 16) ---
BACKTEST_COLUMN_NAMES = [
    "Timestamp", "Setup Uniq", "Pairs", "Direction", "Strategy", "Timeframe",
    "Entry Price", "Stop Loss", "Take Profit", "Position Size", "Leverage", "Status",
    "Exit Price", "PNL (USDT)", "PNL (%)", "Notes"
]


@st.cache_resource(ttl=300)
def get_gsheet_client():
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client

@st.cache_data(ttl=60)
def open_worksheet(_client):
    """
    Membuka GSheet 'Trade Journal' (Sheet1).
    """
    try:
        spreadsheet = _client.open("Trade Journal")
        worksheet = spreadsheet.sheet1
        return worksheet
    except gspread.exceptions.SpreadsheetNotFound:
        st.error("GSheet 'Trade Journal' tidak ditemukan. Pastikan nama file sudah benar dan email bot sudah di-share.")
        return None
    except Exception as e:
        st.error(f"Error saat membuka GSheet 'Trade Journal': {e}")
        return None

# --- Fungsi untuk membuka sheet BackTest ---
@st.cache_data(ttl=60)
def open_backtest_worksheet(_client):
    """
    Membuka GSheet 'Trade Journal' (Sheet: BackTest).
    """
    try:
        spreadsheet = _client.open("Trade Journal")
        worksheet = spreadsheet.worksheet("BackTest") # Buka sheet dengan nama "BackTest"
        return worksheet
    except gspread.exceptions.WorksheetNotFound:
        st.error("Sheet 'BackTest' tidak ditemukan. Pastikan Anda sudah membuat sheet baru dengan nama 'BackTest'.")
        return None
    except Exception as e:
        st.error(f"Error saat membuka sheet 'BackTest': {e}")
        return None

@st.cache_data(ttl=60)
def get_data_as_dataframe(_worksheet, columns):
    """
    Mengambil data dari worksheet. Dibuat generik untuk kedua sheet.
    """
    try:
        data = _worksheet.get_all_values()
        
        if len(data) <= 1:
            return pd.DataFrame(columns=columns) 

        df = pd.DataFrame(data[1:], columns=columns)
        
        # Kolom numerik umum
        numeric_cols = ["Entry Price", "Stop Loss", "Take Profit", "Exit Price", 
                        "Position Size", "PNL (USDT)", "Leverage"]
        
        # Filter hanya kolom numerik yang ada di 'columns'
        cols_to_convert = [col for col in numeric_cols if col in df.columns]
        
        for col in cols_to_convert:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
            
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], format="%Y-%m-%d %H:%M:%S", errors='coerce')
        df = df.dropna(subset=['Timestamp']) 
        
        return df
    except Exception as e:
        st.error(f"Error saat memproses data GSheet: {e}")
        st.info(f"Pastikan nama kolom di GSheet SAMA PERSIS dengan list '{columns}' di kode.")
        return pd.DataFrame()


# -----------------------------------------------------------------
# APLIKASI STREAMLIT
# -----------------------------------------------------------------

st.set_page_config(page_title="Kokpit Trader Pro v3.6", layout="wide")

# --- Custom CSS (Gradien "Dark Ocean") ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
        color: white; 
    }
    h1, h2, h3, h4, h5, h6, .st-b5, .st-b6, .st-at, .st-au, .st-av, .st-aw, .st-ax, .st-ay, .st-az, .st-b0, .st-b1, .st-b2, .st-b3, .st-b4 {
        color: white !important; 
    }
    .stAlert {
        color: black !important; 
    }
    .css-1d391kg e1fqkh3o1 {
        color: white !important;
    }
    .css-pkzbrp.eqr7zpz4 { 
        color: white !important;
    }
    .stSidebar .stSelectbox > label, 
    .stSidebar .stMultiSelect > label {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)
# --------------------------------------------------------------

st.title("🚀 Kokpit Trader Pro v3.6 (Plan -> Backtest -> Log -> Review)")
st.markdown("Dibangun untuk *workflow* trading yang disiplin.")

try:
    client = get_gsheet_client()
    worksheet = open_worksheet(client) if client else None
    backtest_worksheet = open_backtest_worksheet(client) if client else None 

    # Hanya jalankan jika KEDUA sheet berhasil terkoneksi
    if worksheet and backtest_worksheet:
        st.success("✅ Berhasil terkoneksi ke GSheet 'Trade Journal' (Sheet: sheet1 & BackTest)!")

        # [UPDATE v3.6] Menggabungkan Tab 1 & 2. Total 4 Tab
        tab_plan_and_backtest, tab_input_live, tab_backtest_review, tab_dashboard_live = st.tabs([
            "📈 Plan & Backtest", # [BARU v3.6]
            "✍️ Input Trade (Log)", 
            "🔬 Backtest Review", 
            "📊 Dashboard (Review)"
        ])

        # ----------------------------------------------------
        # TAB 1: PLAN & BACKTEST (GABUNGAN)
        # ----------------------------------------------------
        with tab_plan_and_backtest:
            st.header("1. Plan & Eksekusi Backtest")
            st.markdown("Gunakan form ini untuk merencanakan (kalkulasi) DAN mengeksekusi (menyimpan) backtest.")
            
            with st.form(key="plan_and_backtest_form", clear_on_submit=False):
                col_bt_1, col_bt_2, col_bt_3 = st.columns(3)
                
                with col_bt_1:
                    st.subheader("Data Setup")
                    bt_setup_uniq = st.text_input("Setup Uniq*", help="Beri nama unik, e.g., 'BTC 1H Breakout #1'")
                    bt_pairs = st.text_input("Pairs*", help="e.g., BTC/USDT")
                    bt_direction = st.selectbox("Direction*", ["LONG", "SHORT"], key="bt_dir")
                    bt_strategy = st.text_input("Strategy*", help="e.g., Break & Retest")
                    bt_timeframe = st.selectbox("Timeframe*", ["1m", "5m", "15m", "30m", "1H", "4H", "1D"], key="bt_tf")
                
                with col_bt_2:
                    st.subheader("Data Posisi")
                    bt_entry = st.number_input("Entry Price*", value=0.0, format="%.2f")
                    bt_sl = st.number_input("Stop Loss*", value=0.0, format="%.2f")
                    bt_tp = st.number_input("Take Profit*", value=0.0, format="%.2f")
                    bt_position_size = st.number_input("Position Size (USDT)*", value=100.0, help="Total nilai posisi, BUKAN margin", format="%.2f")
                    bt_leverage = st.number_input("Leverage (x)*", min_value=1, step=1, value=20)

                with col_bt_3:
                    st.subheader("Data Kalkulator Likuidasi")
                    bt_margin_type = st.selectbox("Margin Type*", ["Isolated", "Cross"], help="Pilih mode margin Anda.", key="bt_margin_type")
                    
                    if bt_margin_type == 'Isolated':
                        st.info("Leverage (x) sudah diisi di 'Data Posisi'.")
                        bt_equity = 0.0 # Tidak dipakai
                    else: 
                        bt_equity = st.number_input("Total Equity (Wallet)*", value=1000.0, help="Total ekuitas di dompet futures Anda.", format="%.2f", key="bt_equity")
                
                st.divider()
                
                # --- [BARU v3.6] Dua Tombol Aksi ---
                col_btn_1, col_btn_2 = st.columns(2)
                with col_btn_1:
                    calculate_button = st.form_submit_button("Hanya Hitung RRR & Liq. Price")
                
                with col_btn_2:
                    submit_backtest_button = st.form_submit_button("✅ Simpan ke Backtest (Status: Open)")

            # --- Logika setelah form di-submit ---
            
            # Cek validasi dasar (harus diisi semua)
            # [UPDATE v3.6] Validasi gabungan
            is_valid_required = all([bt_setup_uniq, bt_pairs, bt_strategy, bt_entry > 0, bt_sl > 0, bt_tp > 0, bt_position_size > 0, bt_leverage > 0])
            is_valid_liq = (bt_margin_type == 'Isolated') or (bt_margin_type == 'Cross' and bt_equity > 0)
            
            # 1. Jika Tombol "Hanya Hitung" ditekan
            if calculate_button:
                if not is_valid_required or not is_valid_liq:
                    st.error("❌ Semua field (*) wajib diisi dan tidak boleh nol (0). Cek kembali input Anda.")
                elif bt_direction == "LONG" and (bt_entry < bt_sl or bt_entry > bt_tp):
                    st.error("❌ Untuk LONG: SL harus < Entry, dan TP harus > Entry.")
                elif bt_direction == "SHORT" and (bt_entry > bt_sl or bt_entry < bt_tp):
                    st.error("❌ Untuk SHORT: SL harus > Entry, dan TP harus < Entry.")
                else:
                    # --- Lakukan Kalkulasi (tanpa simpan) ---
                    with st.spinner("Menghitung RRR & Likuidasi..."):
                        qty_koin = bt_position_size / bt_entry
                        
                        if bt_direction == "LONG":
                            risk_per_koin = bt_entry - bt_sl
                            reward_per_koin = bt_tp - bt_entry
                        else: 
                            risk_per_koin = bt_sl - bt_entry
                            reward_per_koin = bt_entry - bt_tp
                            
                        risk_dolar = risk_per_koin * qty_koin
                        reward_dolar = reward_per_koin * qty_koin
                        rrr = np.divide(reward_dolar, risk_dolar) if risk_dolar != 0 else 0 
                        
                        liq_price = 0.0
                        if bt_margin_type == 'Isolated':
                            margin_isolated = bt_position_size / bt_leverage
                            if qty_koin != 0: 
                                liq_price = bt_entry - (margin_isolated / qty_koin) if bt_direction == 'LONG' else bt_entry + (margin_isolated / qty_koin)
                        else: # Cross
                            if qty_koin != 0: 
                                liq_price = bt_entry - (bt_equity / qty_koin) if bt_direction == 'LONG' else bt_entry + (bt_equity / qty_koin)
                        
                        st.subheader(f"Hasil Kalkulasi untuk: {bt_setup_uniq}")
                        st.info(f"**Kuantitas Koin:** `{qty_koin:.8f}` (dihitung dari Size / Entry)")
                        
                        col_risk, col_reward, col_rrr = st.columns(3)
                        col_risk.metric("POTENSI RISK", f"${risk_dolar:,.2f}", "Jika kena SL")
                        col_reward.metric("POTENSI REWARD", f"${reward_dolar:,.2f}", "Jika kena TP")
                        col_rrr.metric("Risk/Reward Ratio (RRR)", f"1 : {rrr:.2f}")
                        
                        st.divider()
                        st.metric(label=f"ESTIMASI LIQ. PRICE ({bt_margin_type})", value=f"${liq_price:,.8f}")
                        st.warning("`Perhatian:` Estimasi Liq. Price **TIDAK** termasuk *fees* atau *funding rates*.")

                        if rrr < 2.0:
                            st.warning(f"**RRR RENDAH (1:{rrr:.2f})**: Trade ini mungkin tidak layak dieksekusi.")
                        else:
                            st.success(f"**RRR BAIK (1:{rrr:.2f})**: Setup ini layak disimpan ke backtest.")
            
            # 2. Jika Tombol "Simpan ke Backtest" ditekan
            if submit_backtest_button:
                if not is_valid_required: # Cukup validasi dasar, tak perlu validasi likuidasi
                    st.error("❌ Semua field (*) wajib diisi dan harga/size/leverage tidak boleh nol (0).")
                elif bt_direction == "LONG" and (bt_entry < bt_sl or bt_entry > bt_tp):
                    st.error("❌ Untuk LONG: SL harus < Entry, dan TP harus > Entry.")
                elif bt_direction == "SHORT" and (bt_entry > bt_sl or bt_entry < bt_tp):
                    st.error("❌ Untuk SHORT: SL harus > Entry, dan TP harus < Entry.")
                else:
                    with st.spinner(f"Menyimpan setup '{bt_setup_uniq}' ke GSheet..."):
                        jakarta_tz = pytz.timezone('Asia/Jakarta')
                        timestamp = datetime.now(jakarta_tz).strftime("%Y-%m-%d %H:%M:%S")
                        
                        new_row = [
                            timestamp, bt_setup_uniq, bt_pairs, bt_direction, bt_strategy, bt_timeframe,
                            bt_entry, bt_sl, bt_tp, bt_position_size, bt_leverage, "Open",
                            "", "", "", "" # Exit Price, PNL (USDT), PNL (%), Notes (kosong)
                        ]
                        
                        backtest_worksheet.append_row(new_row)
                        st.cache_data.clear() 
                        st.success(f"✅ Setup '{bt_setup_uniq}' berhasil disimpan (Status: Open).")
                        st.rerun()

            st.divider()
            
            # --- Dashboard Update Backtest ---
            st.header("2. Dashboard & Update Posisi Terbuka")
            
            with st.spinner("Memuat data backtest..."):
                df_bt_raw_for_closing = get_data_as_dataframe(backtest_worksheet, BACKTEST_COLUMN_NAMES)
            
            if df_bt_raw_for_closing.empty:
                st.info("Belum ada data backtest. Silakan input setup pertama Anda.")
            else:
                df_open = df_bt_raw_for_closing[df_bt_raw_for_closing["Status"] == "Open"].copy()
                
                if df_open.empty:
                    st.success("🎉 Selamat! Tidak ada posisi backtest yang terbuka.")
                else:
                    col_dash_bt_1, col_dash_bt_2 = st.columns([2, 1])
                    
                    with col_dash_bt_1:
                        st.markdown("**Posisi Backtest (Status: Open)**")
                        cols_to_show = ["Timestamp", "Setup Uniq", "Pairs", "Direction", "Strategy", "Leverage", "Entry Price", "Stop Loss", "Take Profit"]
                        st.dataframe(df_open[cols_to_show].sort_values(by="Timestamp", ascending=False), width='stretch')
                    
                    with col_dash_bt_2:
                        st.markdown("**Tutup Posisi**")
                        with st.form("close_backtest_form", clear_on_submit=True):
                            setup_to_close = st.selectbox("Pilih Setup Uniq untuk ditutup*", options=df_open["Setup Uniq"].tolist())
                            bt_exit_price = st.number_input("Harga Exit (Close Posisi)*", value=0.0, format="%.2f")
                            bt_notes = st.text_area("Notes / Lesson Learned", help="Apa yang dipelajari dari trade ini?")
                            
                            submit_close_button = st.form_submit_button("Tutup Posisi & Hitung PNL")
                            
                            if submit_close_button:
                                if not setup_to_close or bt_exit_price <= 0:
                                    st.error("❌ Pilih Setup Uniq dan masukkan Harga Exit yang valid.")
                                else:
                                    with st.spinner(f"Menutup posisi '{setup_to_close}'..."):
                                        try:
                                            trade_data = df_open[df_open["Setup Uniq"] == setup_to_close].iloc[0]
                                            sheet_row_index = df_bt_raw_for_closing[df_bt_raw_for_closing["Setup Uniq"] == setup_to_close].index[0] + 2
                                            
                                            entry_price = float(trade_data["Entry Price"])
                                            position_size = float(trade_data["Position Size"])
                                            direction = trade_data["Direction"]
                                            leverage = float(trade_data["Leverage"])
                                            
                                            qty_koin = position_size / entry_price if entry_price != 0 else 0
                                            pnl_usdt = (bt_exit_price - entry_price) * qty_koin if direction == "LONG" else (entry_price - bt_exit_price) * qty_koin
                                            
                                            margin_used = position_size / leverage if leverage != 0 else 0
                                            pnl_percent_float = np.divide(pnl_usdt, margin_used) * 100 if margin_used != 0 else 0
                                            pnl_percent_str = f"{pnl_percent_float:.2f}%"

                                            col_status_index = BACKTEST_COLUMN_NAMES.index("Status") + 1
                                            col_exit_index = BACKTEST_COLUMN_NAMES.index("Exit Price") + 1
                                            col_pnl_usdt_index = BACKTEST_COLUMN_NAMES.index("PNL (USDT)") + 1
                                            col_pnl_percent_index = BACKTEST_COLUMN_NAMES.index("PNL (%)") + 1
                                            col_notes_index = BACKTEST_COLUMN_NAMES.index("Notes") + 1
                                            
                                            updates = [
                                                {'range': f'R{sheet_row_index}C{col_status_index}', 'values': [['Closed']]},
                                                {'range': f'R{sheet_row_index}C{col_exit_index}', 'values': [[bt_exit_price]]},
                                                {'range': f'R{sheet_row_index}C{col_pnl_usdt_index}', 'values': [[round(pnl_usdt, 4)]]},
                                                {'range': f'R{sheet_row_index}C{col_pnl_percent_index}', 'values': [[pnl_percent_str]]},
                                                {'range': f'R{sheet_row_index}C{col_notes_index}', 'values': [[bt_notes]]}
                                            ]
                                            
                                            backtest_worksheet.batch_update(updates, value_input_option='USER_ENTERED')
                                            
                                            st.cache_data.clear() 
                                            st.success(f"✅ Posisi '{setup_to_close}' ditutup!")
                                            if pnl_usdt > 0:
                                                st.success(f"Profit: ${pnl_usdt:,.2f} ({pnl_percent_str})")
                                            else:
                                                st.error(f"Loss: ${pnl_usdt:,.2f} ({pnl_percent_str})")
                                            st.rerun() 
                                            
                                        except Exception as e:
                                            st.error(f"Gagal update GSheet: {e}")
                                            st.error("Pastikan tidak ada orang lain yg sedang mengedit GSheet bersamaan.")


        # ----------------------------------------------------
        # TAB 3: INPUT TRADE (LIVE)
        # ----------------------------------------------------
        with tab_input_live:
            st.header("Catat Trade Baru (Live Trade)")
            st.markdown("Hanya catat trade yang sudah dieksekusi di *exchange*.")
            
            with st.form(key="trade_form", clear_on_submit=True):
                col_input_1, col_input_2, col_input_3 = st.columns(3)
                
                with col_input_1:
                    st.subheader("Data Setup")
                    pairs = st.text_input("Pairs*", help="e.g., BTC/USDT")
                    direction = st.selectbox("Direction*", ["LONG", "SHORT"])
                    timeframe = st.selectbox("Timeframe*", ["1m", "5m", "15m", "30m", "1H", "4H", "1D"])
                    strategy = st.text_input("Strategy", help="e.g., Break & Retest")
                
                with col_input_2:
                    st.subheader("Data Rencana (Plan)")
                    entry_price = st.number_input("Entry Price*", value=0.0, help="Harga Anda masuk", format="%.2f")
                    stop_loss = st.number_input("Stop Loss*", value=0.0, help="Harga cut loss", format="%.2f")
                    take_profit = st.number_input("Take Profit*", value=0.0, help="Harga target", format="%.2f")
                    leverage = st.number_input("Leverage (x)*", min_value=1, step=1, value=20)
                    position_size = st.number_input("Position Size (USDT)*", value=0.0, help="Total nilai posisi, BUKAN margin", format="%.2f")

                with col_input_3:
                    st.subheader("Data Hasil & Psikologis")
                    exit_price = st.number_input("Exit Price*", value=0.0, help="Harga Anda keluar. Ini akan menghitung PNL otomatis.", format="%.2f")
                    setup_quality = st.selectbox("Kualitas Setup", ["A (High-Prob)", "B (Good-Prob)", "C (Low-Prob)"])
                    emotion_pre = st.selectbox("Emosi Pre-Trade", ["Confident", "Anxious", "Calm", "FOMO", "Bored"])
                    emotion_post = st.selectbox("Emosi Post-Trade", ["Happy", "Regret", "Angry", "Calm", "Neutral"])

                st.subheader("Review & Pembelajaran")
                lesson_learned = st.text_area("Lesson Learned (Apa yang harus dilakukan/dihindari?)")

                submit_button = st.form_submit_button(label="Simpan Trade & Hitung PNL")

                if submit_button:
                    if not all([pairs, entry_price > 0, stop_loss > 0, take_profit > 0, position_size > 0, exit_price > 0]):
                        st.error("❌ Data dengan tanda bintang (*) wajib diisi dan tidak boleh nol (0). Cek kembali input harga & size.")
                    else:
                        with st.spinner("Menghitung PNL & RRR (Zona Waktu WIB)..."):
                            jakarta_tz = pytz.timezone('Asia/Jakarta')
                            timestamp = datetime.now(jakarta_tz).strftime("%Y-%m-%d %H:%M:%S")
                            
                            qty_koin = position_size / entry_price if entry_price != 0 else 0
                            pnl_usdt = (exit_price - entry_price) * qty_koin if direction == "LONG" else (entry_price - exit_price) * qty_koin
                            margin_used = position_size / leverage if leverage != 0 else 0
                            pnl_percent = np.divide(pnl_usdt, margin_used) * 100 if margin_used != 0 else 0
                            
                            risk_per_koin = abs(entry_price - stop_loss)
                            reward_per_koin = abs(take_profit - entry_price)
                            rr_ratio = np.divide(reward_per_koin, risk_per_koin) if risk_per_koin > 0 else 0 

                            new_row = [
                                timestamp, pairs, direction, entry_price, stop_loss,
                                take_profit, exit_price, position_size, round(pnl_usdt, 4),
                                f"{pnl_percent:.2f}%", f"1:{rr_ratio:.2f}", leverage,
                                timeframe, strategy, setup_quality, emotion_pre,
                                emotion_post, lesson_learned 
                            ]
                            
                            worksheet.append_row(new_row)
                            st.cache_data.clear() 
                            
                            st.success(f"✅ Trade {pairs} ({direction}) berhasil dicatat! (WIB: {timestamp})")
                            if pnl_usdt > 0:
                                st.balloons()
                                st.success(f"Profit: ${pnl_usdt:,.2f} ({pnl_percent:.2f}%)")
                            else:
                                st.warning(f"Loss: ${pnl_usdt:,.2f} ({pnl_percent:.2f}%) - Review pelajarannya!")
                            st.rerun()


        # ----------------------------------------------------
        # TAB 4: BACKTEST REVIEW
        # ----------------------------------------------------
        with tab_backtest_review:
            st.header("Dashboard Review Performa Backtest")
            st.markdown("Validasi strategi Anda di sini. Apakah Win Rate & Profit Factor-nya sudah layak?")
            
            if st.button("Refresh Data Review Backtest", key="refresh_bt_review"):
                st.cache_data.clear()
                st.success("Cache data backtest di-clear!")
                st.rerun()
            
            with st.spinner("Memuat dan memproses data backtest..."):
                df_bt_raw = get_data_as_dataframe(backtest_worksheet, BACKTEST_COLUMN_NAMES)
                df_bt_closed = df_bt_raw[df_bt_raw["Status"] == "Closed"].copy()
            
            if df_bt_closed.empty:
                st.warning("Data backtest (Closed) masih kosong. Silakan tutup beberapa posisi backtest Anda!")
            else:
                # --- Sidebar Filters untuk Backtest ---
                st.sidebar.header("🔬 Filter Backtest Review")
                
                bt_unique_pairs = df_bt_closed["Pairs"].unique()
                bt_selected_pairs = st.sidebar.multiselect("Filter Pairs (Backtest)", bt_unique_pairs, default=bt_unique_pairs, key="bt_pairs_filter")
                
                bt_unique_strategies = df_bt_closed[df_bt_closed["Strategy"] != '']["Strategy"].unique()
                bt_selected_strategies = st.sidebar.multiselect("Filter Strategi (Backtest)", bt_unique_strategies, default=bt_unique_strategies, key="bt_strat_filter")

                bt_unique_timeframe = df_bt_closed["Timeframe"].unique()
                bt_selected_timeframe = st.sidebar.multiselect("Filter Timeframe (Backtest)", bt_unique_timeframe, default=bt_unique_timeframe, key="bt_tf_filter")

                # Terapkan filter
                df_bt_filtered = df_bt_closed[
                    (df_bt_closed["Pairs"].isin(bt_selected_pairs)) &
                    (df_bt_closed["Strategy"].isin(bt_unique_strategies if not bt_selected_strategies else bt_selected_strategies)) &
                    (df_bt_closed["Timeframe"].isin(bt_selected_timeframe))
                ].copy() 
                
                if df_bt_filtered.empty:
                    st.warning("Tidak ada data backtest yang cocok dengan filter Anda.")
                    st.stop() 

                st.subheader("Analisis Cepat Performa Backtest (Sesuai Filter)")
                
                bt_total_pnl = df_bt_filtered["PNL (USDT)"].sum()
                bt_total_trades = len(df_bt_filtered)
                bt_wins = df_bt_filtered[df_bt_filtered["PNL (USDT)"] > 0]
                bt_losses = df_bt_filtered[df_bt_filtered["PNL (USDT)"] < 0]
                
                bt_total_wins = len(bt_wins)
                bt_total_losses = len(bt_losses)
                bt_win_rate = (bt_total_wins / bt_total_trades) * 100 if bt_total_trades > 0 else 0
                bt_avg_win = bt_wins["PNL (USDT)"].mean() if bt_total_wins > 0 else 0
                bt_avg_loss = abs(bt_losses["PNL (USDT)"].mean()) if bt_total_losses > 0 else 0
                
                bt_total_profit = bt_wins["PNL (USDT)"].sum()
                bt_total_loss_abs = abs(bt_losses["PNL (USDT)"].sum())
                bt_profit_factor = np.divide(bt_total_profit, bt_total_loss_abs) if bt_total_loss_abs > 0 else 999.0 
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total PNL Backtest (USDT)", f"${bt_total_pnl:,.2f}")
                col2.metric("Total Trades Backtest", bt_total_trades)
                col3.metric("Win Rate Backtest", f"{bt_win_rate:.2f}%")
                
                col4, col5, col6 = st.columns(3)
                col4.metric("Avg. Win ($)", f"${bt_avg_win:,.2f}")
                col5.metric("Avg. Loss ($)", f"${bt_avg_loss:,.2f}")
                col6.metric("Profit Factor", f"{bt_profit_factor:,.2f}", help="Total Profit / Total Loss")

                st.divider()

                st.subheader("Equity Curve (Backtest)")
                bt_df_sorted = df_bt_filtered.sort_values(by="Timestamp")
                bt_df_sorted['Cumulative PNL'] = bt_df_sorted["PNL (USDT)"].cumsum()
                st.line_chart(bt_df_sorted, y='Cumulative PNL', x='Timestamp', width='stretch')
                
                
                st.subheader("Analisis Performa Backtest Mendalam")
                
                col_bt_analytic_1, col_bt_analytic_2 = st.columns(2)
                
                with col_bt_analytic_1:
                    st.markdown("**PNL Backtest Berdasarkan Strategi**")
                    bt_pnl_by_strategy = df_bt_filtered[df_bt_filtered["Strategy"] != ''].groupby("Strategy")["PNL (USDT)"].sum().sort_values(ascending=False)
                    st.bar_chart(bt_pnl_by_strategy, width='stretch')

                with col_bt_analytic_2:
                    st.markdown("**PNL Backtest Berdasarkan Timeframe**")
                    bt_pnl_by_tf = df_bt_filtered.groupby("Timeframe")["PNL (USDT)"].sum().sort_values(ascending=False)
                    st.bar_chart(bt_pnl_by_tf, width='stretch')
                
                st.divider()

                with st.expander("Lihat Semua Catatan Backtest (Sesuai Filter & Sudah Ditutup)", expanded=False):
                    st.dataframe(df_bt_filtered.sort_values(by="Timestamp", ascending=False), width='stretch')


        # ----------------------------------------------------
        # TAB 5: DASHBOARD (Review Live Trade)
        # ----------------------------------------------------
        with tab_dashboard_live:
            st.header("Dashboard Performa Trading (Live)")
            st.markdown("Review ini setiap akhir pekan. Data adalah guru terbaik.")
            
            if st.button("Refresh Data Jurnal", key="refresh_live_review"):
                st.cache_data.clear()
                st.success("Cache data jurnal di-clear!")
                st.rerun()
            
            with st.spinner("Memuat dan memproses data dari GSheet..."):
                df_raw = get_data_as_dataframe(worksheet, COLUMN_NAMES)
            
            if df_raw.empty:
                st.warning("Data jurnal masih kosong. Silakan input trade pertama Anda!")
            else:
                # --- Sidebar Filters ---
                st.sidebar.header("📊 Filter Dashboard Jurnal")
                
                unique_pairs = df_raw["Pairs"].unique()
                selected_pairs = st.sidebar.multiselect("Filter Pairs", unique_pairs, default=unique_pairs, key="live_pairs_filter")
                
                unique_strategies = df_raw[df_raw["Strategy"] != '']["Strategy"].unique()
                selected_strategies = st.sidebar.multiselect("Filter Strategi", unique_strategies, default=unique_strategies, key="live_strat_filter")

                unique_setup_quality = df_raw["Setup Quality"].unique()
                selected_setup_quality = st.sidebar.multiselect("Filter Kualitas Setup", unique_setup_quality, default=unique_setup_quality, key="live_setup_filter")

                df = df_raw[
                    (df_raw["Pairs"].isin(selected_pairs)) &
                    (df_raw["Strategy"].isin(unique_strategies if not selected_strategies else selected_strategies)) &
                    (df_raw["Setup Quality"].isin(selected_setup_quality))
                ].copy() 
                
                if df.empty:
                    st.warning("Tidak ada data yang cocok dengan filter Anda.")
                    st.stop() 

                st.subheader("Analisis Cepat Performa (Sesuai Filter)")
                
                total_pnl = df["PNL (USDT)"].sum()
                total_trades = len(df)
                wins = df[df["PNL (USDT)"] > 0]
                losses = df[df["PNL (USDT)"] < 0]
                
                total_wins = len(wins)
                total_losses = len(losses)
                win_rate = (total_wins / total_trades) * 100 if total_trades > 0 else 0
                avg_win = wins["PNL (USDT)"].mean() if total_wins > 0 else 0
                avg_loss = abs(losses["PNL (USDT)"].mean()) if total_losses > 0 else 0
                
                total_profit = wins["PNL (USDT)"].sum()
                total_loss_abs = abs(losses["PNL (USDT)"].sum())
                profit_factor = np.divide(total_profit, total_loss_abs) if total_loss_abs > 0 else 999.0 
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total PNL (USDT)", f"${total_pnl:,.2f}")
                col2.metric("Total Trades", total_trades)
                col3.metric("Win Rate", f"{win_rate:.2f}%")
                
                col4, col5, col6 = st.columns(3)
                col4.metric("Avg. Win ($)", f"${avg_win:,.2f}")
                col5.metric("Avg. Loss ($)", f"${avg_loss:,.2f}")
                col6.metric("Profit Factor", f"{profit_factor:,.2f}", help="Total Profit / Total Loss")

                st.divider()

                st.subheader("Equity Curve (Kumulatif PNL)")
                df_sorted = df.sort_values(by="Timestamp")
                df_sorted['Cumulative PNL'] = df_sorted["PNL (USDT)"].cumsum()
                st.line_chart(df_sorted, y='Cumulative PNL', x='Timestamp', width='stretch')
                
                
                st.subheader("Analisis Performa Mendalam")
                
                col_analytic_1, col_analytic_2, col_analytic_3 = st.columns(3)
                
                with col_analytic_1:
                    st.markdown("**PNL Berdasarkan Strategi**")
                    pnl_by_strategy = df[df["Strategy"] != ''].groupby("Strategy")["PNL (USDT)"].sum().sort_values(ascending=False)
                    st.bar_chart(pnl_by_strategy, width='stretch')

                with col_analytic_2:
                    st.markdown("**PNL Berdasarkan Kualitas Setup**")
                    pnl_by_setup = df.groupby("Setup Quality")["PNL (USDT)"].sum().sort_values(ascending=False)
                    st.bar_chart(pnl_by_setup, width='stretch')

                with col_analytic_3:
                    st.markdown("**PNL Berdasarkan Emosi Pre-Trade**")
                    pnl_by_emotion = df.groupby("Emotion Pre-Trade")["PNL (USDT)"].sum().sort_values(ascending=False)
                    st.bar_chart(pnl_by_emotion, width='stretch')
                
                st.markdown("`Insight:` Cek strategi, kualitas setup, dan emosi mana yang paling profit/rugi.")
                st.divider()

                with st.expander("Lihat Semua Catatan Trade (Sesuai Filter)", expanded=False):
                    st.dataframe(df.sort_values(by="Timestamp", ascending=False), width='stretch')
                
                st.subheader("Pelajaran Penting (Review)")
                col_lesson_1, col_lesson_2 = st.columns(2)
                
                with col_lesson_1:
                    st.success("Top 3 Wins")
                    top_wins = df.sort_values(by="PNL (USDT)", ascending=False).head(3)
                    for _, row in top_wins.iterrows():
                        st.write(f"**${row['PNL (USDT)']:,.2f}** - {row['Pairs']} ({row['Strategy']})")
                        st.caption(f"Lesson: {row['Lesson Learned']}")
                
                with col_lesson_2:
                    st.error("Top 3 Losses")
                    top_losses = df.sort_values(by="PNL (USDT)", ascending=True).head(3)
                    for _, row in top_losses.iterrows():
                        st.write(f"**${row['PNL (USDT)']:,.2f}** - {row['Pairs']} ({row['Strategy']})")
                        st.caption(f"Lesson: {row['Lesson Learned']}")

except Exception as e:
    if "gcp_service_account" in str(e):
        st.error("Error: 'gcp_service_account' tidak ditemukan di Streamlit Secrets. Pastikan 'secrets.toml' Anda sudah benar.")
    elif "SpreadsheetNotFound" in str(e):
        st.error("Error: GSheet 'Trade Journal' tidak ditemukan. Cek nama file dan pastikan email bot sudah di-share.")
    elif "WorksheetNotFound" in str(e):
         st.error("Error: Sheet 'BackTest' tidak ditemukan. Pastikan Anda sudah membuat sheet baru di GSheet Anda dengan nama 'BackTest'.")
    elif "Mismatched" in str(e) or "column count" in str(e):
        st.error(f"Error: Jumlah kolom GSheet tidak cocok dengan kode. Error: {e}")
        st.error(f"Pastikan Sheet 1 punya {len(COLUMN_NAMES)} kolom & Sheet BackTest punya {len(BACKTEST_COLUMN_NAMES)} kolom.")
    else:
        st.error(f"Terjadi Error. Cek koneksi atau detail GSheet Anda.")
        st.error(f"Error detail: {e}")
