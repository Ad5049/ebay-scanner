import streamlit as st
import requests
import pandas as pd
import time

# Telegram Configuration
TELEGRAM_BOT_TOKEN = "8082987823:AAFSf_5mDnsb5T1cE5_i90B1tO0-yI-Q8l4"
TELEGRAM_CHAT_ID = "8179645246"

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code == 200
    except Exception:
        return False

st.title("eBay High-Margin Arbitrage Scanner")
st.markdown("Scans active listings under target costs, compares against median verified sold values, and instantly pushes alerts for `>=50%` profit margins.")

# Sidebar controls
st.sidebar.header("Scanner Settings")
target_query = st.sidebar.text_input("Target Query", "vintage game boy")
max_cost = st.sidebar.number_input("Max Item Cost ($)", value=50.0)
scan_interval = st.sidebar.number_input("Scan Interval (seconds)", value=60, min_value=30)
auto_scan = st.sidebar.checkbox("Enable Continuous Auto-Scan", value=True)

st.markdown(f"**Current Target Query:** `{target_query}` (Max Item Cost: `${max_cost:.1f}`)")

# Initialize session state for tracking sent alerts to prevent duplicates
if "sent_items" not in st.session_state:
    st.session_state.sent_items = set()

# Simulated live scan function (Replace this with real eBay Browse API calls later)
def run_scanner_pass():
    scanned_listings = [
        {"id": "item_001", "Item": "Nintendo Game Boy Color - Atomic Purple (Untested)", "Cost ($)": 40, "Est. Sold Value ($)": 95, "Margin (%)": 57.8},
        {"id": "item_002", "Item": "Vintage Texas Instruments TI-84 Plus Graphing Calculator", "Cost ($)": 32, "Est. Sold Value ($)": 75, "Margin (%)": 57.3}
    ]
    
    qualified = []
    for item in scanned_listings:
        if item["Cost ($)"] <= max_cost and item["Margin (%)"] >= 50.0:
            qualified.append(item)
            if item["id"] not in st.session_state.sent_items:
                alert_msg = (
                    f"🚨 *New High-Margin Listing Found!*\n\n"
                    f"📦 *Item:* {item['Item']}\n"
                    f"💵 *Cost:* ${item['Cost ($)']}\n"
                    f"📈 *Est. Sold:* ${item['Est. Sold Value ($)']}\n"
                    f"🔥 *Margin:* {item['Margin (%)']}%"
                )
                success = send_telegram_alert(alert_msg)
                if success:
                    st.session_state.sent_items.add(item["id"])
                    
    return pd.DataFrame(qualified)

# Execute scan pass
df_results = run_scanner_pass()

st.subheader("Qualified High-Margin Listings")
if not df_results.empty:
    st.dataframe(df_results[["Item", "Cost ($)", "Est. Sold Value ($)", "Margin (%)"]], use_container_width=True)
else:
    st.info("Scanning for listings matching criteria...")

# Manual Test Button
if st.button("Test Telegram Push Alert"):
    if send_telegram_alert("🚨 *eBay Scanner Test Alert*: Successfully connected to Andrew's bot!"):
        st.success("Test alert pushed to Telegram successfully!")
    else:
        st.error("Failed to push alert. Check your Telegram network settings.")

# Continuous auto-scan loop trigger
if auto_scan:
    st.markdown("---")
    st.info(f"🔄 Auto-scanner active. Re-checking listings every {scan_interval} seconds...")
    time.sleep(scan_interval)
    st.rerun()
    
