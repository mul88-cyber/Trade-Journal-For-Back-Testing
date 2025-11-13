import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from datetime import datetime

# -----------------------------------------------------------------
# KONEKSI KE GOOGLE SHEETS
# -----------------------------------------------------------------

# Kita 'scope' (lingkup) izin yang kita butuhkan
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Fungsi untuk autentikasi dan konek ke GSheet
# Streamlit akan 'inject' secrets dari st.secrets
def get_gsheet_client():
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client

# Fungsi untuk membuka worksheet spesifik
def open_worksheet(client):
    # Buka GSheet berdasarkan NAMA FILE
    spreadsheet = client.open("Trade Journal") 
    # Buka sheet pertama (worksheet)
    worksheet = spreadsheet.sheet1 
    return worksheet

# -----------------------------------------------------------------
# APLIKASI STREAMLIT
# -----------------------------------------------------------------

st.set_page_config(page_title="Kokpit Trader Pro", layout="wide")
st.title("🚀 Kokpit Trader Pro Anda")
st.markdown("Dibangun untuk *workflow* trading yang disiplin.")

try:
    # Coba konek ke GSheet
    client = get_gsheet_client()
    worksheet = open_worksheet(client)
    st.success("Berhasil terkoneksi ke Google Sheet 'Trade Journal' Anda!")

    # Buat TABS untuk navigasi
    tab_input, tab_dashboard = st.tabs(["✍️ Input Trade", "📊 Dashboard"])

    # ----------------------------------------------------
    # TAB 1: INPUT TRADE
    # ----------------------------------------------------
    with tab_input:
        st.header("Catat Trade Baru")
        
        # Gunakan st.form untuk 'batch' input
        with st.form(key="trade_form", clear_on_submit=True):
            
            # Kita pakai kolom biar rapi
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("Data Setup")
                pairs = st.text_input("Pairs (e.g., BTC/USDT)")
                direction = st.selectbox("Direction", ["LONG", "SHORT"])
                timeframe = st.selectbox("Timeframe", ["1m", "5m", "15m", "30m", "1H", "4H", "1D"])
                strategy = st.text_input("Strategy (e.g., Break & Retest)")
                tags = st.text_input("Tags (pisah dgn koma, e.g., FOMC, News, High-RR)")
            
            with col2:
                st.subheader("Data Eksekusi")
                entry_price = st.number_input("Entry Price", format="%.8f")
                stop_loss = st.number_input("Stop Loss", format="%.8f")
                take_profit = st.number_input("Take Profit", format="%.8f")
                leverage = st.number_input("Leverage (x)", min_value=1, step=1, value=20)
                position_size = st.number_input("Position Size (USDT)")

            with col3:
                st.subheader("Data Hasil & Psikologis")
                exit_price = st.number_input("Exit Price (isi jika sudah close)", format="%.8f", value=0.0)
                pnl_usdt = st.number_input("PNL (USDT) (isi jika sudah close)", value=0.0)
                setup_quality = st.selectbox("Kualitas Setup", ["A (High-Prob)", "B (Good-Prob)", "C (Low-Prob)"])
                emotion_pre = st.selectbox("Emosi Pre-Trade", ["Confident", "Anxious", "Calm", "FOMO", "Bored"])
                emotion_post = st.selectbox("Emosi Post-Trade", ["Happy", "Regret", "Angry", "Calm", "Neutral"])

            st.subheader("Review & Pembelajaran")
            learning = st.text_area("Learning (Apa yang terjadi?)")
            lesson_learned = st.text_area("Lesson Learned (Apa yang harus dilakukan/dihindari?)")

            # Tombol Submit
            submit_button = st.form_submit_button(label="Simpan Trade ke Jurnal")

            # Aksi saat tombol submit ditekan
            if submit_button:
                with st.spinner("Menyimpan data..."):
                    
                    # 1. Generate data yang tidak di-input manual
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # 2. Hitung PNL(%) dan R/R Ratio (basic)
                    # Ini bisa Anda kembangkan jadi lebih canggih
                    pnl_percent = (pnl_usdt / position_size) * 100 if position_size > 0 else 0
                    
                    risk = abs(entry_price - stop_loss)
                    reward = abs(take_profit - entry_price)
                    rr_ratio = reward / risk if risk > 0 else 0
                    
                    # 3. Susun data SESUAI URUTAN HEADER GSheet Anda (A-S)
                    new_row = [
                        timestamp,
                        pairs,
                        direction,
                        entry_price,
                        stop_loss,
                        take_profit,
                        exit_price,
                        position_size,
                        pnl_usdt,
                        f"{pnl_percent:.2f}%",  # PNL (%)
                        f"1:{rr_ratio:.2f}",    # R/R_ratio
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
                    
                    # 4. Kirim ke Google Sheet
                    worksheet.append_row(new_row)
                    
                    st.success(f"Trade {pairs} ({direction}) berhasil dicatat! Terus disiplin, bro.")


    # ----------------------------------------------------
    # TAB 2: DASHBOARD
    # ----------------------------------------------------
    with tab_dashboard:
        st.header("Dashboard Performa Trading")
        st.markdown("Ini adalah 'Kotak Hitam' Anda. Review setiap akhir pekan.")
        
        with st.spinner("Memuat data dari GSheet..."):
            # Ambil SEMUA data dari GSheet
            data = worksheet.get_all_records()
            
            if not data:
                st.warning("Data jurnal masih kosong. Silakan input trade pertama Anda!")
            else:
                # Konversi ke Pandas DataFrame
                df = pd.DataFrame(data)
                
                st.subheader("Semua Catatan Trade")
                st.dataframe(df.tail(20)) # Tampilkan 20 trade terakhir
                
                st.divider()
                
                # --- Mulai Analisis Canggih (Ini baru permulaan) ---
                st.subheader("Analisis Cepat Performa")
                
                # Pastikan PNL adalah angka (float)
                df["PNL_(USDT)"] = pd.to_numeric(df["PNL_(USDT)"], errors='coerce').fillna(0)
                
                total_pnl = df["PNL_(USDT)"].sum()
                total_trades = len(df)
                
                # Hitung Win/Loss
                wins = df[df["PNL_(USDT)"] > 0]
                losses = df[df["PNL_(USDT)"] < 0]
                breakeven = df[df["PNL_(USDT)"] == 0]
                
                win_rate = (len(wins) / total_trades) * 100 if total_trades > 0 else 0
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total PNL (USDT)", f"${total_pnl:,.2f}")
                col2.metric("Total Trades", total_trades)
                col3.metric("Win Rate", f"{win_rate:.2f}%")
                
                # Chart Equity Curve (Kumulatif PNL)
                st.subheader("Equity Curve (Kumulatif PNL)")
                df['Cumulative PNL'] = df["PNL_(USDT)"].cumsum()
                st.line_chart(df, y='Cumulative PNL', x='Timestamp')
                
                # Analisis Psikologis (Contoh)
                st.subheader("Analisis Emosi Pre-Trade")
                pnl_by_emotion = df.groupby("Emotion_pre_trade_Confident/Anxious/Calm")["PNL_(USDT)"].sum()
                st.bar_chart(pnl_by_emotion)
                st.markdown("`Insight:` Cek emosi mana yang paling sering menghasilkan *loss*.")


except Exception as e:
    st.error(f"Koneksi Gagal. Cek 3 hal: (1) API sudah 'Enabled'?, (2) Email Bot sudah 'Share' & 'Editor' di GSheet?, (3) 'secrets.toml' sudah benar?")
    st.error(f"Error detail: {e}")
