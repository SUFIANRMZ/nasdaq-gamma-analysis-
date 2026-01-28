import os
import json
import requests
from datetime import datetime

SYMBOL = os.getenv("TARGET_SYMBOL", "QQQ")
TOKEN = os.getenv("TRADIER_ACCESS_TOKEN")

if not TOKEN:
    raise SystemExit("❌ TRADIER_ACCESS_TOKEN ما كاينش فـ secrets")

BASE_URL = "https://api.tradier.com/v1"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json"
}

def get_expirations(symbol):
    url = f"{BASE_URL}/markets/options/expirations"
    r = requests.get(url, headers=HEADERS, params={
        "symbol": symbol,
        "includeAllRoots": "true"
    })
    r.raise_for_status()
    data = r.json()
    dates = data.get("expirations", {}).get("date", [])
    if isinstance(dates, str):
        dates = [dates]
    return dates

def get_chain(symbol, expiration):
    url = f"{BASE_URL}/markets/options/chains"
    r = requests.get(url, headers=HEADERS, params={
        "symbol": symbol,
        "expiration": expiration,
        "greeks": "true"
    })
    r.raise_for_status()
    return r.json().get("options", {}).get("option", [])

def main():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    out_dir = "data/raw"
    os.makedirs(out_dir, exist_ok=True)

    print(f"📥 Collecting options data for {SYMBOL}")

    expirations = get_expirations(SYMBOL)
    all_options = []

    for exp in expirations[:5]:  # خليه 5 باش ما تضربش limit
        chain = get_chain(SYMBOL, exp)
        if chain:
            all_options.extend(chain)

    if not all_options:
        raise SystemExit("❌ ما تجبد حتى option")

    output = {
        "symbol": SYMBOL,
        "date": today,
        "options": all_options
    }

    path = f"{out_dir}/{today}_{SYMBOL}.json"
    with open(path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"✅ Saved {len(all_options)} options → {path}")

if __name__ == "__main__":
    main()
