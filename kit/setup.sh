#!/bin/sh
# Prepara l'ambiente per il kit (Playwright + Chromium + Pillow). Da lanciare una volta per sessione.
python3 -c "import playwright, PIL" 2>/dev/null || pip install --break-system-packages -q playwright pillow
python3 - <<'PY' || python3 -m playwright install chromium
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); b.close()
print("chromium ok")
PY
fc-list | grep -qi "emoji" && echo "emoji ok" || echo "ATTENZIONE: font emoji mancante: usa foto al posto delle emoji o segnala a Valerio"
