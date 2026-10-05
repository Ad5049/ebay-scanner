import streamlit as st
import requests
import pandas as pd
import time

# Discord Webhook URL (Shared across your alert streams)
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1556663289465938010/vb-kGgqjeCwRY3e0LXrL4Dr0IKH7BYLLnfZwUjGoap3E7aPDyYjO1sF3csPFwcJgniTi"

def send_discord_alert(message):
    payload = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        return response.status_code in [200, 204], response.text
    except Exception as e:
        return False, str(e)

st.title("eBay Arbitrage Scanner")
st.markdown("Scanning high-margin listings under $100 with a minimum 50% profit margin and pushing live alerts to Discord.")

# Sidebar controls
st.sidebar.header("Scanner Settings")
max_price = st.sidebar.number_input("Max Listing Price ($)", value=100.0)
min_margin = st.sidebar.slider("Minimum Profit Margin (%)", min_value=10.0, max_value=200.0, value=50.0)
scan_interval = st.sidebar.number_input("Scan Interval (seconds)", value=300, min_value=60)

# Initialize session state for tracking sent items and timestamps
if "sent_ebay_items" not in st.session_state:
    st.session_state.sent_ebay_items = set()
if "last_scan_time" not in st.session_state:
    st.session_state.last_scan_time = 0

def run_ebay_scanner():
    # Placeholder simulation for eBay API / scraping logic matching your parameters
    qualified = []
    
    # Example structured result item for illustration/placeholder integration
    # (Integrate your specific eBay search / Browse API query here)
    sample_item = {
        "Title": "Sample Arbitrage Item",
        "Price": 45.00,
        "Estimated Value": 120.00,
        "Margin (%)": 166.7,
        "Link": "https://www.ebay.com"
    }
    
    if sample_item["Margin (%)"] >= min_margin and sample_item["Price"] <= max_price:
        qualified.append(sample_item)
        item_id = sample_item["Title"]
        
        if item_id not in st.session_state.sent_ebay_items:
            alert_msg = (
                f"🛒 **High-Margin eBay Deal Found!**\n"
                f"📦 **Item:** {sample_item['Title']}\n"
                f"💵 **Price:** ${sample_item['Price']:.2f}\n"
                f"📈 **Estimated Value:** ${sample_item['Estimated Value']:.2f}\n"
                f"🔥 **Profit Margin:** +{sample_item['Margin (%)']:.1f}%\n"
                f"🔗 {sample_item['Link']}"
            )
            success, _ = send_discord_alert(alert_msg)
            if success:
                st.session_state.sent_ebay_items.add(item_id)
                
    return pd.DataFrame(qualified)

# Rate-limited automatic execution block
current_time = time.time()
if current_time - st.session_state.last_scan_time > scan_interval:
    st.session_state.last_scan_time = current_time
    st.rerun()

df_results = run_ebay_scanner()

st.subheader("Live Flagged eBay Opportunities")
if not df_results.empty:
    st.dataframe(
        df_results[["Title", "Price", "Estimated Value", "Margin (%)", "Link"]],
        column_config={"Link": st.column_config.LinkColumn("eBay Link")},
        use_container_width=True
    )
else:
    st.info("Scanning eBay listings for high-margin arbitrage opportunities...")

if st.button("Test eBay Discord Alert"):
    success, api_response = send_discord_alert("🛒 **eBay Scanner Test Alert**: Successfully connected to Discord!")
    if success:
        st.success("Test alert pushed successfully to Discord!")
    else:
        st.error(f"Webhook Error Response: {api_response}")
        
