from ib_insync import IB, Stock, MarketOrder  # imported for compatibility if you ever enable IB
import time
import logging
import os
from dotenv import load_dotenv
import random
from datetime import datetime

# -----------------------------
# Load Environment Variables
# -----------------------------
load_dotenv()

DRY_RUN = os.getenv("DRY_RUN", "true").lower() in ("1", "true", "yes")
IB_HOST = os.getenv("IB_HOST", "127.0.0.1")
IB_PORT = int(os.getenv("IB_PORT", 7497))
IB_CLIENT_ID = int(os.getenv("IB_CLIENT_ID", 1))
TRADE_SYMBOL = os.getenv("TRADE_SYMBOL", "AAPL")
TRADE_CURRENCY = os.getenv("TRADE_CURRENCY", "USD")
TRADE_EXCHANGE = os.getenv("TRADE_EXCHANGE", "SMART")

# -----------------------------
# Logging Setup
# -----------------------------
print("🚀 IB Gateway Bot (updated) has started...")
print("🔌 Mode:", "DRY RUN (no IB connection)" if DRY_RUN else "LIVE / PAPER (will try to connect)")

logging.basicConfig(
    filename='ib_gateway_bot.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logging.info("🚀 IB Gateway Bot started (DRY_RUN=%s)" % DRY_RUN)

# -----------------------------
# IB Connection Object
# -----------------------------
ib = IB()

def connect_ib():
    """Connect to Interactive Brokers only if not in DRY_RUN mode."""
    if DRY_RUN:
        print("🟡 DRY RUN — Skipping IB.connect()")
        logging.info("DRY RUN — connection skipped.")
        return True

    print("🔄 Connecting to IB Gateway...")
    try:
        if not ib.isConnected():
            ib.connect(IB_HOST, IB_PORT, clientId=IB_CLIENT_ID)
            print("✅ Connected to IB Gateway")
            logging.info("✅ Connected to IB Gateway")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        logging.error(f"❌ Connection failed: {e}")
        return False

def place_trade(symbol):
    """Place a trade — actually sends to IB only if DRY_RUN is False."""
    try:
        # Prepare random trade parameters
        action = random.choice(['BUY', 'SELL'])
        qty = random.randint(1, 5)
        timestamp = datetime.now().isoformat(timespec='seconds')

        if DRY_RUN:
            # Simulate an order id and fill info
            fake_order_id = random.randint(100000, 999999)
            msg = f"🟢 [DRY] Simulated {action} {qty} {symbol} (orderId={fake_order_id}) at {timestamp}"
            print(msg)
            logging.info(msg)
            return {"status": "simulated", "action": action, "qty": qty, "symbol": symbol, "orderId": fake_order_id}

        # LIVE/PAPER flow (real IB paper/live order)
        stock = Stock(symbol, TRADE_EXCHANGE, TRADE_CURRENCY)
        ib.qualifyContracts(stock)

        order = MarketOrder(action, qty)
        trade = ib.placeOrder(stock, order)
        ib.sleep(2)

        msg = f"✅ Placed {action} order for {qty} {symbol} at {ib.reqCurrentTime()}"
        print(msg)
        logging.info(msg)
        return {"status": "placed", "action": action, "qty": qty, "symbol": symbol}

    except Exception as e:
        err = f"❌ Trade Error: {e}"
        print(err)
        logging.error(err)
        return {"status": "error", "error": str(e)}

# -----------------------------
# Main Loop
# -----------------------------
if __name__ == "__main__":
    try:
        ok = connect_ib()
        if not ok and not DRY_RUN:
            print("❌ IB connection failed and DRY_RUN is disabled. Exiting.")
            logging.error("IB connection failed; exiting.")
            raise SystemExit(1)

        while True:
            result = place_trade(TRADE_SYMBOL)

            # Test-friendly short delay; change to minutes for real runs
            wait_time = random.randint(10, 20)
            print(f"⏳ Next action in {wait_time} seconds...\n")
            logging.info(f"Sleeping for {wait_time} seconds (DRY_RUN={DRY_RUN})")
            time.sleep(wait_time)

    except KeyboardInterrupt:
        print("🛑 Bot manually stopped (KeyboardInterrupt).")
        logging.info("🛑 Bot stopped by user.")
    except Exception as e:
        print(f"⚠️ Unexpected Error: {e}")
        logging.error(f"⚠️ Unexpected Error: {e}")
