import json
import os
from datetime import datetime

SYMBOL = os.getenv("TARGET_SYMBOL", "QQQ")
today = datetime.utcnow().strftime("%Y-%m-%d")

path = f"data/raw/{today}_{SYMBOL}.json"

if not os.path.exists(path):
    raise SystemExit("❌ ملف الداتا ما لقاهاش")

with open(path) as f:
    data = json.load(f)

options = data.get("options", [])
if not options:
    raise SystemExit("❌ Options فارغين")

TOTAL_GEX = 0

for opt in options:
    gamma = opt.get("greeks", {}).get("gamma")
    oi = opt.get("open_interest")

    if gamma is None or oi is None:
        continue

    sign = -1 if opt.get("option_type") == "put" else 1
    TOTAL_GEX += sign * gamma * oi * 100

out_dir = "data/processed"
os.makedirs(out_dir, exist_ok=True)

out_path = f"{out_dir}/{today}_{SYMBOL}_gex.json"
with open(out_path, "w") as f:
    json.dump({
        "symbol": SYMBOL,
        "date": today,
        "total_gex": TOTAL_GEX
    }, f, indent=2)

print(f"✅ GEX calculated: {TOTAL_GEX:.2f}")
