import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

st.title("🔍 Google Sheets Connection Test")

st.markdown("## Test 1: Check Secrets")
try:
    # Check if secrets exist
    st.write("✅ Secrets file found")
    
    # Check spreadsheet_id
    if "spreadsheet_id" in st.secrets:
        st.write(f"✅ Spreadsheet ID: `{st.secrets['spreadsheet_id']}`")
    else:
        st.error("❌ spreadsheet_id not found in secrets!")
    
    # Check service account
    if "gcp_service_account" in st.secrets:
        st.write("✅ Service account credentials found")
        st.write(f"   - Client Email: `{st.secrets['gcp_service_account']['client_email']}`")
        st.write(f"   - Project ID: `{st.secrets['gcp_service_account']['project_id']}`")
    else:
        st.error("❌ gcp_service_account not found in secrets!")
        
except Exception as e:
    st.error(f"❌ Error reading secrets: {e}")

st.markdown("---")
st.markdown("## Test 2: Connect to Google Sheets")

try:
    # Initialize credentials
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    client = gspread.authorize(credentials)
    st.write("✅ Successfully created credentials")
    
    # Try to open spreadsheet
    sheet = client.open_by_key(st.secrets["spreadsheet_id"]).sheet1
    st.write("✅ Successfully connected to Google Sheet")
    
    # Get sheet info
    st.write(f"   - Sheet title: `{sheet.spreadsheet.title}`")
    st.write(f"   - Worksheet title: `{sheet.title}`")
    st.write(f"   - Total rows: `{sheet.row_count}`")
    st.write(f"   - Total columns: `{sheet.col_count}`")
    
except gspread.exceptions.SpreadsheetNotFound:
    st.error("❌ Spreadsheet not found! Kemungkinan:")
    st.error("   1. Spreadsheet ID salah")
    st.error("   2. Sheet belum di-share dengan service account")
    
except gspread.exceptions.APIError as e:
    st.error(f"❌ Google API Error: {e}")
    st.error("   Pastikan Google Sheets API & Drive API sudah di-enable")
    
except Exception as e:
    st.error(f"❌ Connection error: {e}")

st.markdown("---")
st.markdown("## Test 3: Read Headers")

try:
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(st.secrets["spreadsheet_id"]).sheet1
    
    # Get first row (headers)
    headers = sheet.row_values(1)
    
    if headers:
        st.write("✅ Found headers:")
        for i, header in enumerate(headers, 1):
            st.write(f"   Column {i}: `{header}`")
        
        # Check expected headers
        st.markdown("### Expected Headers:")
        expected = ['Buy Date', 'Stock Code', 'Qty Lot', 'Price (Buy)', 'Value (Buy)', 
                   'Current Date', 'Current Price', 'Custom Date', 'Custom Price', 
                   'Possition', 'Change %', 'P&L', 'Change % (Custom)', 'P&L (Custom)']
        
        missing = []
        for exp in expected:
            if exp in headers:
                st.write(f"   ✅ `{exp}`")
            else:
                st.write(f"   ❌ `{exp}` - MISSING!")
                missing.append(exp)
        
        if missing:
            st.error(f"⚠️ Missing headers: {', '.join(missing)}")
            st.error("Tambahkan header yang hilang di Row 1 Google Sheet!")
    else:
        st.error("❌ No headers found! Pastikan Row 1 ada header nya")
        
except Exception as e:
    st.error(f"❌ Error reading headers: {e}")

st.markdown("---")
st.markdown("## Test 4: Try to Write Data")

if st.button("🧪 Test Write to Sheet"):
    try:
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )
        client = gspread.authorize(credentials)
        sheet = client.open_by_key(st.secrets["spreadsheet_id"]).sheet1
        
        # Try to append test row
        test_row = [
            "2025-02-15",  # Buy Date
            "TEST",        # Stock Code
            1,             # Qty Lot
            1000,          # Price (Buy)
            "",            # Value (Buy)
            "",            # Current Date
            "",            # Current Price
            "",            # Custom Date
            "",            # Custom Price
            "OPEN",        # Possition
            "",            # Change %
            "",            # P&L
            "",            # Change % (Custom)
            ""             # P&L (Custom)
        ]
        
        sheet.append_row(test_row)
        st.success("✅ Successfully wrote test data to Google Sheet!")
        st.balloons()
        st.info("Cek Google Sheet kamu, seharusnya ada row baru dengan Stock Code 'TEST'")
        
    except gspread.exceptions.APIError as e:
        st.error(f"❌ API Error: {e}")
        if "PERMISSION_DENIED" in str(e):
            st.error("⚠️ Service account tidak punya permission untuk write!")
            st.error("Pastikan service account di-share dengan role EDITOR (bukan Viewer)")
    except Exception as e:
        st.error(f"❌ Write error: {e}")

st.markdown("---")
st.markdown("## 📝 Instructions")
st.info("""
**Jika ada error, ikuti langkah berikut:**

1. **Spreadsheet Not Found** → 
   - Pastikan Spreadsheet ID benar
   - Share Google Sheet dengan: `streamlit-to-gdrive@stock-analysis-461503.iam.gserviceaccount.com`
   - Role: Editor

2. **Permission Denied** →
   - Service account role harus EDITOR (bukan Viewer)
   - Re-share dengan role Editor

3. **Missing Headers** →
   - Tambahkan header yang hilang di Row 1
   - Pastikan spelling exact (termasuk spasi)

4. **API Error** →
   - Pastikan Google Sheets API sudah di-enable
   - Pastikan Google Drive API sudah di-enable
""")
