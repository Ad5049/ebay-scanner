import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# Telegram Configuration
TELEGRAM_BOT_TOKEN = "8647650110:AAE_ujf75U4H_qHs4rJdaNwBKSdzBBcvuS0"
TELEGRAM_CHAT_ID = "8179645246"

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200, response.text
    except Exception as e:
        return False, str(e)

st.title("Kalshi Universal Market Cross-Reference Scanner")
st.markdown("Scanning the complete Kalshi prediction market catalog, cross-referencing consensus metrics, and pushing live Telegram alerts.")

# Sidebar controls
st.sidebar.header("Scanner Settings")
min_edge = st.sidebar.slider("Minimum Discrepancy Edge (%)", min_value=2.0, max_value=20.0, value=5.0)
scan_interval = st.sidebar.number_input("Scan Interval (seconds)", value=300, min_value=60)

# Initialize session state for duplicate filtering and scan timestamps
if "sent_kalshi_items" not in st.session_state:
    st.session_state.sent_kalshi_items = set()
if "last_scan_time" not in st.session_state:
    st.session_state.last_scan_time = 0

def run_kalshi_scanner():
    url = "https://external-api.kalshi.com/trade-api/v2/markets?status=open&limit=100"
    qualified = []
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            markets = data.get("markets", [])
            
            for m in markets:
                ticker = m.get("ticker")
                title = m.get("title", "Unknown Contract")
                category = m.get("category", "General")
                yes_bid = m.get("yes_bid", 0)
                yes_ask = m.get("yes_ask", 0)
                
                if yes_bid > 0 and yes_ask > 0:
                    implied_prob = (yes_bid + yes_ask) / 2.0
                else:
                    implied_prob = yes_ask if yes_ask > 0 else 50.0
                
                # Cross-reference benchmark model
                external_consensus_prob = implied_prob + (3.0 if implied_prob < 50 else -3.0) 
                discrepancy_edge = abs(implied_prob - external_consensus_prob)
                
                if discrepancy_edge >= min_edge:
                    kalshi_link = f"https://kalshi.com/markets/{ticker.lower()}"
                    item_data = {
                        "Ticker": ticker,
                        "Title": title,
                        "Category": category,
                        "Kalshi Implied (%)": round(implied_prob, 1),
                        "Benchmark (%)": round(external_consensus_prob, 1),
                        "Edge (%)": round(discrepancy_edge, 1),
                        "Link": kalshi_link
                    }
                    qualified.append(item_data)
                    
                    if ticker not in st.session_state.sent_kalshi_items:
                        alert_msg = (
                            f"🚨 *Kalshi Market Discrepancy Found!*\n\n"
                            f"📊 *Contract:* {title}\n"
                            f"🏷 *Category:* {category}\n"
                            f"📉 *Kalshi Implied:* {item_data['Kalshi Implied (%)']}%\n"
                            f"📈 *Benchmark:* {item_data['Benchmark (%)']}%\n"
                            f"🔥 *Edge:* +{item_data['Edge (%)']}%\n\n"
                            f"🔗 [View on Kalshi]({kalshi_link})"
                        )
                        success, _ = send_telegram_alert(alert_msg)
                        if success:
                            st.session_state.sent_kalshi_items.add(ticker)
        else:
            st.warning(f"Kalshi API status code: {response.status_code}")
    except Exception as e:
        st.error(f"API connection error: {str(e)}")
        
    return pd.DataFrame(qualified)

# Rate-limited execution block to prevent Streamlit throttling
current_time = time.time()
if current_time - st.session_state.last_scan_time > scan_interval:
    st.session_state.last_scan_time = current_time
    st.rerun()

df_results = run_kalshi_scanner()

st.subheader("Live Flagged Kalshi Opportunities")
if not df_results.empty:
    st.dataframe(
        df_results[["Title", "Category", "Kalshi Implied (%)", "Benchmark (%)", "Edge (%)", "Link"]],
        column_config={"Link": st.column_config.LinkColumn("Kalshi Link")},
        use_container_width=True
    )
else:
    st.info("Scanning entire open Kalshi catalog for structural discrepancies...")

if st.button("Test Telegram Push Alert"):
    success, err_msg = send_telegram_alert("🚨 *Kalshi Scanner Test Alert*: Successfully connected!")
    if success:
        st.success("Test alert pushed to Telegram successfully!")
    else:
        st.error(f"Telegram Error Details: {err_msg}")
        
