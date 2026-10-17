"""Stamp local CSS/JS references with a content hash (?v=...) so browsers never
run a stale cached copy after an update. Run after editing styles.css, main.js
or flight.js:   python3 tools/version_assets.py
"""
import glob, hashlib, re
from pathlib import Path

root = Path(__file__).resolve().parent.parent
assets = ['styles.css', 'main.js', 'flight.js']
ver = {a: hashlib.md5((root / a).read_bytes()).hexdigest()[:8] for a in assets}
for page in glob.glob(str(root / '*.html')):
    h = open(page).read()
    for a in assets:
        h = re.sub(r'((?:href|src)="(?:/astrabeam-site/)?)' + re.escape(a) + r'(\?v=[0-9a-f]+)?"',
                   lambda m, a=a: f'{m.group(1)}{a}?v={ver[a]}"', h)
    open(page, 'w').write(h)
print('versions:', ver)
