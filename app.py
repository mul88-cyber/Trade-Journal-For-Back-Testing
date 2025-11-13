import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from datetime import datetime
import numpy as np # Kita pakai numpy untuk handle pembagian 0

# -----------------------------------------------------------------
# KONEKSI KE GOOGLE SHEETS
# -----------------------------------------------------------------

# Kita 'scope' (lingkup) izin yang kita butuhkan
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Fungsi untuk autentikasi dan konek ke GSheet
def get_gsheet_client():
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client

# Fungsi untuk membuka worksheet spesifik
def open_worksheet(client):
    try:
        spreadsheet = client.open("Trade Journal") 
        worksheet = spreadsheet.sheet1 
        return worksheet
    except gspread.exceptions.SpreadsheetNotFound:
        st.error("GSheet 'Trade Journal' tidak ditemukan. Pastikan nama file sudah benar dan email bot sudah di-share.")
        return None
    except Exception as e:
        st.error(f"Error saat membuka GSheet: {e}")
        return None

# -----------------------------------------------------------------
# APLIKASI STREAMLIT
# -----------------------------------------------------------------

st.set_page_config(page_title="Kokpit Trader Pro v2.0", layout="wide")
st.title("🚀 Kokpit Trader Pro v2.0 (Otomatis)")
st.markdown("Dibangun untuk *workflow* trading yang disiplin.")

try:
    # Coba konek ke GSheet
    client = get_gsheet_client()
    if client:
        worksheet = open_worksheet(client)
    else:
        worksheet = None

    if worksheet:
        st.success("Berhasil terkoneksi ke Google Sheet 'Trade Journal' Anda!")

        # Buat TABS untuk navigasi
        tab_input, tab_dashboard = st.tabs(["✍️ Input Trade (Otomatis)", "📊 Dashboard"])

        # ----------------------------------------------------
        # TAB 1: INPUT TRADE (DIOPTIMALKAN)
        # ----------------------------------------------------
        with tab_input:
            st.header("Catat Trade Baru")
            st.markdown("Isi **Rencana** (Entry, SL, TP) dan **Hasil** (Exit). Biarkan sistem menghitung PNL & RRR.")
            
            with st.form(key="trade_form", clear_on_submit=True):
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.subheader("Data Setup")
                    pairs = st.text_input("Pairs*", help="e.g., BTC/USDT")
                    direction = st.selectbox("Direction*", ["LONG", "SHORT"])
                    timeframe = st.selectbox("Timeframe*", ["1m", "5m", "15m", "30m", "1H", "4H", "1D"])
                    strategy = st.text_input("Strategy", help="e.g., Break & Retest")
                    tags = st.text_input("Tags (pisah dgn koma)", help="e.g., FOMC, News")
                
                with col2:
                    st.subheader("Data Rencana (Plan)")
                    entry_price = st.number_input("Entry Price*", format="%.8f", help="Harga Anda masuk")
                    stop_loss = st.number_input("Stop Loss*", format="%.8f", help="Harga cut loss")
                    take_profit = st.number_input("Take Profit*", format="%.8f", help="Harga target")
                    leverage = st.number_input("Leverage (x)*", min_value=1, step=1, value=20)
                    position_size = st.number_input("Position Size (USDT)*", help="Total nilai posisi, BUKAN margin")

                with col3:
                    st.subheader("Data Hasil & Psikologis")
                    # INI KUNCINYA: HANYA INPUT EXIT PRICE
                    exit_price = st.number_input("Exit Price*", format="%.8f", help="Harga Anda keluar. Ini akan menghitung PNL otomatis.")
                    setup_quality = st.selectbox("Kualitas Setup", ["A (High-Prob)", "B (Good-Prob)", "C (Low-Prob)"])
                    emotion_pre = st.selectbox("Emosi Pre-Trade", ["Confident", "Anxious", "Calm", "FOMO", "Bored"])
                    emotion_post = st.selectbox("Emosi Post-Trade", ["Happy", "Regret", "Angry", "Calm", "Neutral"])

                st.subheader("Review & Pembelajaran")
                learning = st.text_area("Learning (Apa yang terjadi?)")
                lesson_learned = st.text_area("Lesson Learned (Apa yang harus dilakukan/dihindari?)")

                submit_button = st.form_submit_button(label="Simpan Trade & Hitung PNL")

                if submit_button:
                    # Validasi input dasar
                    if not all([pairs, entry_price > 0, stop_loss > 0, take_profit > 0, position_size > 0, exit_price > 0]):
                        st.error("Data dengan tanda bintang (*) wajib diisi dan tidak boleh nol.")
                    else:
                        with st.spinner("Menghitung PNL & RRR..."):
                            
                            # --- LOGIKA KALKULASI OTOMATIS ---
                            
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                            # 1. Hitung Kuantitas Koin
                            # Qty = Posisi (USDT) / Harga Entry
                            qty_koin = position_size / entry_price
                            
                            # 2. Hitung PNL (USDT)
                            if direction == "LONG":
                                pnl_usdt = (exit_price - entry_price) * qty_koin
                            else: # SHORT
                                pnl_usdt = (entry_price - exit_price) * qty_koin
                                
                            # 3. Hitung Margin yang Digunakan
                            # Margin = Posisi (USDT) / Leverage
                            margin_used = position_size / leverage
                            
                            # 4. Hitung PNL (%)
                            # PNL% = PNL (USDT) / Margin
                            # Kita pakai np.divide untuk menghindari error jika margin 0
                            pnl_percent = np.divide(pnl_usdt, margin_used) * 100
                            
                            # 5. Hitung R/R Ratio (Planned)
                            risk_per_koin = abs(entry_price - stop_loss)
                            reward_per_koin = abs(take_profit - entry_price)
                            
                            # Hindari pembagian nol jika SL = Entry
                            rr_ratio = np.divide(reward_per_koin, risk_per_koin)

                            # --- AKHIR LOGIKA KALKULASI ---

                            # Susun data SESUAI URUTAN HEADER GSheet Anda (A-S)
                            new_row = [
                                timestamp,
                                pairs,
                                direction,
                                entry_price,
                                stop_loss,
                                take_profit,
                                exit_price,
                                position_size,
                                round(pnl_usdt, 4),           # PNL_(USDT) - Otomatis
                                f"{pnl_percent:.2f}%",        # PNL_(%) - Otomatis
                                f"1:{rr_ratio:.2f}",          # R/R_ratio - Otomatis
                                leverage,
                                setup_quality,
                                emotion_pre,
                                emotion_post,
                                learning,
                                lesson_learned,
                                timeframe,
                                strategy,
                                tags
                            ]
                            
                            # Kirim ke Google Sheet
                            worksheet.append_row(new_row)
                            
                            st.success(f"Trade {pairs} ({direction}) berhasil dicatat!")
                            if pnl_usdt > 0:
                                st.balloons()
                                st.success(f"Profit: ${pnl_usdt:.2f} ({pnl_percent:.2f}%)")
                            else:
                                st.warning(f"Loss: ${pnl_usdt:.2f} ({pnl_percent:.2f}%) - Review pelajarannya!")


        # ----------------------------------------------------
        # TAB 2: DASHBOARD
        # ----------------------------------------------------
        with tab_dashboard:
            st.header("Dashboard Performa Trading")
            st.markdown("Review ini setiap akhir pekan. Data adalah guru terbaik.")
            
            with st.spinner("Memuat data dari GSheet..."):
                data = worksheet.get_all_records()
                
                if not data:
                    st.warning("Data jurnal masih kosong. Silakan input trade pertama Anda!")
                else:
                    df = pd.DataFrame(data)
                    
                    # --- Data Cleaning (PENTING untuk Dashboard) ---
                    # 1. Konversi PNL_(USDT) ke angka
                    df["PNL_(USDT)"] = pd.to_numeric(df["PNL_(USDT)"], errors='coerce').fillna(0)
                    
                    # 2. Konversi Timestamp ke format datetime
                    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
                    
                    # --- Tampilan Dashboard ---
                    st.subheader("Semua Catatan Trade (20 Terakhir)")
                    # Urutkan dari terbaru
                    st.dataframe(df.sort_values(by="Timestamp", ascending=False).head(20))
                    
                    st.divider()
                    
                    st.subheader("Analisis Cepat Performa")
                    
                    total_pnl = df["PNL_(USDT)"].sum()
                    total_trades = len(df)
                    
                    wins = df[df["PNL_(USDT)"] > 0]
                    losses = df[df["PNL_(USDT)"] < 0]
                    
                    total_wins = len(wins)
                    total_losses = len(losses)
                    
                    win_rate = (total_wins / total_trades) * 100 if total_trades > 0 else 0
                    
                    # Rata-rata Win/Loss (Profit Factor)
                    avg_win = wins["PNL_(USDT)"].mean() if total_wins > 0 else 0
                    avg_loss = abs(losses["PNL_(USDT)"].mean()) if total_losses > 0 else 0
                    profit_factor = (wins["PNL_(USDT)"].sum() / abs(losses["PNL_(USDT)"].sum())) if total_losses > 0 else 0
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total PNL (USDT)", f"${total_pnl:,.2f}")
                    col2.metric("Total Trades", total_trades)
                    col3.metric("Win Rate", f"{win_rate:.2f}%")
                    
                    col4, col5, col6 = st.columns(3)
                    col4.metric("Avg. Win ($)", f"${avg_win:,.2f}")
                    col5.metric("Avg. Loss ($)", f"${avg_loss:,.2f}")
                    col6.metric("Profit Factor", f"{profit_factor:,.2f}", help="Total Profit / Total Loss")

                    # Chart Equity Curve (Kumulatif PNL)
                    st.subheader("Equity Curve (Kumulatif PNL)")
                    df_sorted = df.sort_values(by="Timestamp") # Urutkan berdasarkan waktu
                    df_sorted['Cumulative PNL'] = df_sorted["PNL_(USDT)"].cumsum()
                    st.line_chart(df_sorted, y='Cumulative PNL', x='Timestamp')
                    
                    # Analisis Psikologis
                    st.subheader("Analisis PNL berdasarkan Emosi Pre-Trade")
                    pnl_by_emotion = df.groupby("Emotion_pre_trade_Confident/Anxious/Calm")["PNL_(USDT)"].sum()
                    st.bar_chart(pnl_by_emotion)
                    st.markdown("`Insight:` Cek emosi mana yang paling sering menghasilkan *loss*. Jika 'FOMO' minus banyak, Anda tahu apa yang harus diperbaiki.")

except Exception as e:
    st.error(f"Terjadi Error. Cek 3 hal: (1) API sudah 'Enabled'?, (2) Email Bot sudah 'Share' & 'Editor' di GSheet?, (3) 'secrets.toml' sudah benar?")
    st.error(f"Error detail: {e}")
