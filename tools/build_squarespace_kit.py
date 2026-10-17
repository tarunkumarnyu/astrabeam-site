"""Build the Squarespace paste-in kit from index.html.

    python3 tools/build_squarespace_kit.py

Writes squarespace/*.html. Every asset (videos, images, CSS, JS, flight data)
is loaded from the GitHub Pages copy of this repo, so push to GitHub before
pasting a rebuilt kit. Re-run tools/version_assets.py first if CSS/JS changed.
"""
import re
from pathlib import Path

BASE = 'https://tarunkumarnyu.github.io/astrabeam-site'
root = Path(__file__).resolve().parent.parent
out = root / 'squarespace'
out.mkdir(exist_ok=True)
html = (root / 'index.html').read_text()


def absolutize(s):
    """Point relative asset/script/style references at the GitHub Pages host."""
    s = re.sub(r'((?:src|href|poster)=")(assets/|styles\.css|main\.js|flight\.js|privacy\.html)',
               lambda m: m.group(1) + BASE + '/' + m.group(2), s)
    return s


def between(a, b):
    i = html.index(a)
    j = html.index(b, i)
    return html[i:j]


def version(name):
    m = re.search(re.escape(name) + r'\?v=([0-9a-f]+)', html)
    return m.group(1) if m else 'dev'


# ---------- 1. page header code injection ----------
fonts = re.search(r'<link href="https://fonts\.googleapis\.com/css2[^"]+" rel="stylesheet">', html).group(0)
importmap = re.search(r'<script type="importmap">.*?</script>', html, re.S).group(0)
header = f'''<!-- Astrabeam homepage: Page Settings > Advanced > Page Header Code Injection -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{fonts}
<link rel="stylesheet" href="{BASE}/styles.css?v={version('styles.css')}">
{importmap}
<style>
  /* Hide Squarespace's own header and footer on this page: the page brings its own. */
  #header, header.header, .header-announcement-bar-wrapper, #footer-sections, footer.sections {{ display: none !important; }}
  /* Let the code blocks run edge to edge. */
  #page .page-section {{ padding: 0 !important; min-height: 0 !important; }}
  #page .page-section .content-wrapper {{ padding: 0 !important; max-width: none !important; }}
  #page .sqs-block-code, #page .sqs-block-code .sqs-block-content {{ padding: 0 !important; margin: 0 !important; }}
  #page .fluid-engine {{ row-gap: 0 !important; }}
  body {{ background: #0a0b0d !important; }}
  /* Contact code block holds only heading + details; the Form Block sits beside it. */
  .contact-grid.contact-only {{ grid-template-columns: 1fr; }}
  .contact.section {{ padding-bottom: 40px; }}
  .site-wrapper, #siteWrapper {{ background: #0a0b0d; }}

  /* Native Squarespace Form Block, restyled to match the design (contact section). */
  #page .sqs-block-form form {{ font-family: "Inter Tight", system-ui, sans-serif; }}
  #page .sqs-block-form .form-wrapper, #page .sqs-block-form .form-inner-wrapper {{ background: transparent !important; }}
  #page .sqs-block-form label, #page .sqs-block-form .title, #page .sqs-block-form legend {{
    color: #8a9099 !important; font-size: 14px !important; font-weight: 400 !important; letter-spacing: 0 !important; text-transform: none !important;
  }}
  #page .sqs-block-form input[type=text], #page .sqs-block-form input[type=email], #page .sqs-block-form input[type=tel],
  #page .sqs-block-form textarea, #page .sqs-block-form select {{
    background: #111317 !important; border: 1px solid #2c3138 !important; border-radius: 0 !important;
    color: #ecedef !important; font: 16px "Inter Tight", sans-serif !important; padding: 12px 14px !important; box-shadow: none !important;
  }}
  #page .sqs-block-form input:focus, #page .sqs-block-form textarea:focus, #page .sqs-block-form select:focus {{ border-color: #ff6600 !important; outline: none !important; }}
  #page .sqs-block-form select {{
    -webkit-appearance: none !important; appearance: none !important; height: 46px; padding-right: 44px !important;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1.5 6 6.5 11 1.5' fill='none' stroke='%23ff6600' stroke-width='1.6'/%3E%3C/svg%3E") !important;
    background-repeat: no-repeat !important; background-position: right 16px center !important;
  }}
  #page .sqs-block-form button[type=submit], #page .sqs-block-form .form-button-wrapper button {{
    background: #ff6600 !important; color: #0a0b0d !important; border: 0 !important; border-radius: 0 !important;
    font: 500 16px "Inter Tight", sans-serif !important; padding: 14px 24px !important; text-transform: none !important; letter-spacing: 0 !important;
  }}
  #page .sqs-block-form button[type=submit]:hover {{ background: #ff8533 !important; }}
  #page .sqs-block-form .form-submission-text {{ color: #ecedef !important; }}
</style>
<script defer src="{BASE}/main.js?v={version('main.js')}"></script>
<script type="module" src="{BASE}/flight.js?v={version('flight.js')}"></script>
'''
(out / '1-page-header-code-injection.html').write_text(header)

# ---------- 2. main code block: nav through news ----------
main = between('<header class="nav">', '<section class="section contact"')
main = main.replace('<section class="section flight" id="flight">',
                    f'<section class="section flight" id="flight" data-flight="{BASE}/assets/flight/flight.json">')
main = absolutize(main)
(out / '2-code-block-main.html').write_text('<!-- Code Block 1 (HTML mode): everything from the nav to News -->\n' + main)

# ---------- 3. contact code block (details only; the form is a native Form Block) ----------
contact = between('<section class="section contact"', '<footer class="footer">')
contact = re.sub(r'\s*<!-- Preview of the contact form.*?</form>', '', contact, flags=re.S)
contact = contact.replace('<div class="wrap contact-grid">', '<div class="wrap contact-grid contact-only">')
(out / '3-code-block-contact.html').write_text(
    '<!-- Code Block 2 (HTML mode): contact heading and details. Put the native Form Block next to it. -->\n'
    + absolutize(contact))

# ---------- 4. footer code block ----------
footer = between('<footer class="footer">', '<script')
(out / '4-code-block-footer.html').write_text('<!-- Code Block 3 (HTML mode): footer -->\n' + absolutize(footer).replace(
    f'{BASE}/privacy.html', '/privacy'))

sizes = {p.name: p.stat().st_size for p in sorted(out.glob('*.html'))}
for k, v in sizes.items():
    print(f'{k:40s} {v/1024:6.1f} KB' + ('   <-- over Squarespace 400 KB code-block limit!' if v > 400_000 else ''))
