import urllib.request
import ssl
import certifi
import os
import re
from datetime import datetime

BASE_URL = "https://opendata.dwd.de/weather/radar/radolan/rw"
OUTPUT_DIR = "data/radar"
os.makedirs(OUTPUT_DIR, exist_ok=True)

ssl_context = ssl.create_default_context(cafile=certifi.where())

# ======================
# Verzeichnis laden
# ======================
with urllib.request.urlopen(BASE_URL + "/", context=ssl_context) as response:
    html = response.read().decode("utf-8")

# ======================
# Dateien finden:
# - hdf5
# - Minute == 50
# ======================
pattern = re.compile(
    r'raa01-rw_10000-(\d{10})-dwd---bin\.hdf5'
)

files = []

for match in pattern.finditer(html):
    ts_str = match.group(1)  # z.B. 2602081250
    dt = datetime.strptime(ts_str, "%y%m%d%H%M")

    if dt.minute == 50:
        files.append((dt, match.group(0)))

if not files:
    raise RuntimeError("Keine passende 50er-Datei gefunden")

# ======================
# Neueste Datei wählen
# ======================
files.sort(key=lambda x: x[0])
dt, filename = files[-1]

url = f"{BASE_URL}/{filename}"
print("Downloading:", url)

# ======================
# Download
# ======================
with urllib.request.urlopen(url, context=ssl_context, timeout=30) as response:
    data = response.read()

output_path = os.path.join(
    OUTPUT_DIR,
    f"radolan-rw-{dt.strftime('%Y%m%d-%H%M')}.hdf5"
)

with open(output_path, "wb") as f:
    f.write(data)

print("Saved:", output_path)
