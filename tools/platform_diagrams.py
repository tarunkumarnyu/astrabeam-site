"""Generate the four platform-layer diagrams (inline SVG) for index.html.

Run:  python3 tools/platform_diagrams.py   (rewrites the block between the
<!-- LAYERS:START --> and <!-- LAYERS:END --> markers in index.html)

Diagrams are illustrative; they carry no performance numbers.
"""
import random
from pathlib import Path

ORANGE, DIM, LINE, MUTED, FG, GREEN, RED = '#ff6600', '#7c838d', '#2a3038', '#4a515b', '#eceef1', '#3dffa8', '#ff4d4d'
MONO = "font-family=\"IBM Plex Mono, monospace\""
W, H = 560, 300


def svg(pid, body, label):
    return f'''<svg class="diag-svg" viewBox="0 0 {W} {H}" role="img" aria-label="{label}" xmlns="http://www.w3.org/2000/svg">
<defs>
  <pattern id="{pid}-dots" width="16" height="16" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".9" fill="{LINE}"/></pattern>
  <pattern id="{pid}-hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" stroke="#3a4048" stroke-width="1"/></pattern>
  <linearGradient id="{pid}-beam" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="{ORANGE}" stop-opacity=".45"/><stop offset="1" stop-color="{ORANGE}" stop-opacity="0"/></linearGradient>
  <linearGradient id="{pid}-fog" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#5f656c"/><stop offset="1" stop-color="#2b2f34"/></linearGradient>
</defs>
{body}
</svg>'''


def text(x, y, s, color=DIM, size=9, anchor='start', weight=400):
    return f'<text x="{x}" y="{y}" {MONO} font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}" letter-spacing=".08em">{s}</text>'


def bracket(x, y, w, h, c=10, color=ORANGE):
    return (f'<path d="M{x} {y+c}V{y}H{x+c} M{x+w-c} {y}H{x+w}V{y+c} M{x+w} {y+h-c}V{y+h}H{x+w-c} '
            f'M{x+c} {y+h}H{x}V{y+h-c}" fill="none" stroke="{color}" stroke-width="1.5"/>')


def hardware():
    rnd = random.Random(7)
    b = []
    # radar module with a 4x4 antenna array
    b.append(f'<rect x="40" y="105" width="90" height="90" fill="#0d0f12" stroke="{MUTED}"/>')
    b.append(f'<rect x="34" y="99" width="102" height="102" fill="none" stroke="{LINE}" stroke-dasharray="2 3"/>')
    for i in range(4):
        for j in range(4):
            d = (i + j) * 0.12
            b.append(f'<rect x="{51+i*19}" y="{116+j*19}" width="11" height="11" fill="none" stroke="{ORANGE}" stroke-opacity=".85">'
                     f'<animate attributeName="stroke-opacity" values=".35;1;.35" dur="2.4s" begin="{d:.2f}s" repeatCount="indefinite"/></rect>')
        b.append(text(40, 92, 'RF FRONT END', MUTED))
    # obscurants
    for _ in range(70):
        x, y, r = rnd.uniform(190, 430), rnd.uniform(30, 270), rnd.uniform(1, 3.2)
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#6b727b" fill-opacity="{rnd.uniform(.18,.5):.2f}"/>')
    b.append(text(200, 286, 'SMOKE · FOG · DUST'))
    # sweeping beam
    b.append(f'<g><path d="M132 150 L540 70 L540 230 Z" fill="url(#hw-beam)"/>'
             f'<line x1="132" y1="150" x2="448" y2="150" stroke="{ORANGE}" stroke-opacity=".5" stroke-dasharray="3 5"/>'
             f'<animateTransform attributeName="transform" type="rotate" values="-11 132 150;11 132 150;-11 132 150" dur="6s" repeatCount="indefinite"/></g>')
    # target: person silhouette with returns
    b.append(f'<g fill="none" stroke="{FG}" stroke-opacity=".75" stroke-width="1.4">'
             f'<circle cx="478" cy="118" r="9"/><path d="M466 176 V140 Q466 130 478 130 Q490 130 490 140 V176 M470 176 V210 M486 176 V210"/></g>')
    for y in (112, 124, 138, 150, 162, 176, 190, 204):
        b.append(f'<circle cx="{466 if y>130 else 469}" cy="{y}" r="2" fill="{ORANGE}"><animate attributeName="opacity" values="0;1;0" dur="6s" begin="{(y-112)/40:.2f}s" repeatCount="indefinite"/></circle>')
    b.append(bracket(452, 100, 52, 118))
    b.append(text(452, 92, 'TARGET', ORANGE))
    for k in range(2):
        b.append(f'<circle cx="478" cy="160" r="10" fill="none" stroke="{ORANGE}"><animate attributeName="r" values="10;46" dur="3s" begin="{k*1.5}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="stroke-opacity" values=".6;0" dur="3s" begin="{k*1.5}s" repeatCount="indefinite"/></circle>')
    return svg('hw', '\n'.join(b), 'Sub-terahertz radar beam sweeping through smoke and dust to detect a person')


PATH = 'M60 250 C 120 250, 140 170, 200 165 S 290 220, 330 160 S 380 70, 450 80 S 505 70, 512 62'


def software():
    b = []
    for x, y, w, h in [(150, 195, 70, 70), (235, 60, 80, 70), (318, 196, 52, 58), (380, 25, 40, 40), (40, 70, 70, 60)]:
        b.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#sw-hatch)" stroke="#3a4048"/>')
    b.append(f'<path d="{PATH}" fill="none" stroke="{ORANGE}" stroke-opacity=".12" stroke-width="6" stroke-linecap="round"/>')
    b.append(f'<path d="{PATH}" fill="none" stroke="{ORANGE}" stroke-width="1.6" stroke-dasharray="5 6">'
             f'<animate attributeName="stroke-dashoffset" values="0;-22" dur="1s" repeatCount="indefinite"/></path>')
    b.append(f'<circle cx="60" cy="250" r="5" fill="none" stroke="{FG}"/>' + text(48, 278, 'START'))
    b.append(f'<rect x="504" y="54" width="16" height="16" fill="none" stroke="{GREEN}"/><path d="M512 46V78M496 62H528" stroke="{GREEN}" stroke-opacity=".6"/>' + text(484, 98, 'GOAL', GREEN))
    # robot with onboard sensing cone, moving along the path
    b.append(f'<g><path d="M0 0 L42 -18 L42 18 Z" fill="{ORANGE}" fill-opacity=".14"/>'
             f'<g stroke="{FG}" stroke-width="1.6"><line x1="-7" y1="-7" x2="7" y2="7"/><line x1="-7" y1="7" x2="7" y2="-7"/></g>'
             f'<circle r="2.4" fill="{ORANGE}"/>'
             f'<animateMotion dur="9s" repeatCount="indefinite" rotate="auto" path="{PATH}"/></g>')
    # status panel
    b.append(f'<rect x="392" y="196" width="152" height="88" fill="#0d0f12" stroke="{MUTED}"/>')
    rows = [('GNSS', 'DENIED', RED), ('LINK', 'LOST', RED), ('PRIOR MAP', 'NONE', RED), ('NAV', 'ONBOARD', GREEN)]
    for i, (k, v, c) in enumerate(rows):
        y = 216 + i * 19
        b.append(text(404, y, k) + text(532, y, v, c, anchor='end', weight=500))
    return svg('sw', '\n'.join(b), 'Robot navigating around obstacles to a goal with GPS denied, communication lost and no prior map, using onboard perception')


def ml():
    rnd = random.Random(3)
    b = []
    # inputs
    b.append(f'<rect x="24" y="42" width="128" height="88" fill="#0d0f12" stroke="{MUTED}"/>' + text(24, 34, 'RADAR'))
    for _ in range(46):
        x, y = rnd.uniform(34, 142), rnd.uniform(70, 122)
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.3" fill="{ORANGE}" fill-opacity="{rnd.uniform(.4,1):.2f}"/>')
    b.append(f'<path d="M40 120 Q 88 58 136 120" fill="none" stroke="{ORANGE}" stroke-opacity=".35"/>')
    b.append(f'<rect x="24" y="170" width="128" height="88" fill="url(#ml-fog)" stroke="{MUTED}"/>' + text(24, 162, 'CAMERA'))
    b.append(f'<path d="M40 240 L70 205 L92 228 L112 212 L136 240 Z" fill="#1d2025" fill-opacity=".5"/>')
    b.append(text(88, 252, 'LOW VISIBILITY', '#c9cdd2', size=8, anchor='middle'))
    # network
    cols = [[70, 110, 150, 190, 230], [90, 130, 170, 210], [110, 150, 190]]
    xs = [220, 285, 350]
    edges = []
    for ci in range(len(cols) - 1):
        for y1 in cols[ci]:
            for y2 in cols[ci + 1]:
                edges.append((xs[ci], y1, xs[ci + 1], y2))
    for y in cols[0]:
        edges += [(152, 86, xs[0], y), (152, 214, xs[0], y)]
    for y in cols[-1]:
        edges.append((xs[-1], y, 396, 150))
    for x1, y1, x2, y2 in edges:
        b.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{LINE}"/>')
    for ci, ys in enumerate(cols):
        for y in ys:
            b.append(f'<circle cx="{xs[ci]}" cy="{y}" r="5" fill="#0d0f12" stroke="{MUTED}"/>')
    b.append(text(285, 268, 'MULTI-MODAL FUSION', anchor='middle'))
    # moving activations
    for k, (x1, y1, x2, y2) in enumerate([(152, 86, 220, 110), (220, 110, 285, 130), (285, 130, 350, 150), (350, 150, 396, 150),
                                          (152, 214, 220, 190), (220, 190, 285, 170), (285, 170, 350, 150)]):
        dl = (k % 4) * 0.45
        b.append(f'<circle r="2.6" fill="{ORANGE}"><animateMotion dur="1.8s" begin="{dl:.2f}s" repeatCount="indefinite" path="M{x1} {y1}L{x2} {y2}"/></circle>')
    # output
    b.append(f'<rect x="396" y="48" width="144" height="204" fill="#0d0f12" stroke="{MUTED}"/>' + text(396, 40, 'SCENE UNDERSTANDING'))
    b.append(f'<path d="M408 236 L440 214 L470 220 L500 196 L528 180" fill="none" stroke="{GREEN}" stroke-dasharray="2 4"/>')
    for x, y in [(408, 236), (440, 214), (470, 220), (500, 196), (528, 180)]:
        b.append(f'<circle cx="{x}" cy="{y}" r="2" fill="{GREEN}"/>')
    b.append(text(408, 248, 'NAVIGATION PATH', GREEN, size=8))
    b.append(bracket(410, 78, 44, 74) + text(410, 72, 'PERSON', ORANGE, size=8))
    b.append(bracket(466, 112, 62, 46) + text(466, 106, 'VEHICLE', ORANGE, size=8))
    return svg('ml', '\n'.join(b), 'Radar and camera inputs fused by a neural network into detections and a navigation path')


def deployment():
    b = []
    # edge compute board
    bx, by = 210, 92
    b.append(f'<rect x="{bx}" y="{by}" width="140" height="116" fill="#0d0f12" stroke="{MUTED}"/>')
    for i in range(9):
        b.append(f'<line x1="{bx+14+i*12}" y1="{by+12}" x2="{bx+14+i*12}" y2="{by+34}" stroke="{MUTED}"/>')
    b.append(f'<rect x="{bx+44}" y="{by+46}" width="52" height="40" fill="none" stroke="{ORANGE}"/>'
             f'<rect x="{bx+56}" y="{by+56}" width="28" height="20" fill="{ORANGE}" fill-opacity=".18"/>')
    for i in range(6):
        b.append(f'<rect x="{bx+10+i*21}" y="{by+100}" width="12" height="8" fill="none" stroke="{MUTED}"/>')
    b.append(text(bx + 70, by + 136, 'EDGE COMPUTE', FG, anchor='middle', weight=500))
    b.append(text(bx + 70, by + 150, 'JETSON-CLASS', DIM, anchor='middle'))
    b.append(text(bx + 70, by - 12, 'OPEN LOOP AUTONOMY', ORANGE, anchor='middle'))
    # platforms
    plats = {
        'drone': (70, 62, 'UAV'),
        'rover': (70, 238, 'GROUND ROBOT'),
        'amr': (488, 150, 'AMR'),
    }
    b.append('<g stroke="#c9cdd2" stroke-width="1.4" fill="none">'
             '<line x1="52" y1="48" x2="88" y2="76"/><line x1="52" y1="76" x2="88" y2="48"/>'
             '<circle cx="52" cy="48" r="8"/><circle cx="88" cy="48" r="8"/><circle cx="52" cy="76" r="8"/><circle cx="88" cy="76" r="8"/>'
             '<rect x="44" y="222" width="52" height="22"/><circle cx="54" cy="250" r="7"/><circle cx="86" cy="250" r="7"/><path d="M58 222 V212 H74"/>'
             '<rect x="468" y="132" width="40" height="34"/><circle cx="476" cy="170" r="4"/><circle cx="500" cy="170" r="4"/><path d="M508 140 H522 V124"/>'
             '</g>')
    for key, (x, y, lab) in plats.items():
        b.append(text(x, y + {'drone': 40, 'rover': 30, 'amr': 42}[key], lab, DIM, anchor='middle'))
    links = [f'M{bx} {by+30} C 160 {by+30}, 130 64, 100 64', f'M{bx} {by+90} C 160 {by+90}, 130 236, 100 236',
             f'M{bx+140} {by+58} C 420 {by+58}, 430 150, 464 150']
    for k, d in enumerate(links):
        b.append(f'<path d="{d}" fill="none" stroke="{MUTED}" stroke-dasharray="3 4"/>')
        b.append(f'<circle r="2.6" fill="{ORANGE}"><animateMotion dur="2.4s" begin="{k*0.6:.1f}s" repeatCount="indefinite" path="{d}"/></circle>')
    b.append(text(250, 24, 'INTEGRATES WITH EXISTING STACKS', DIM))
    # pilot -> fleet: 1 unit, 3 units, a fleet; groups spaced so connectors never touch squares
    groups = [(392, 1), (434, 3), (500, 6)]
    for i, (gx, n) in enumerate(groups):
        for j in range(n):
            x, y = gx + (j % 3) * 12, 246 + (j // 3) * 12
            b.append(f'<rect x="{x}" y="{y}" width="8" height="8" fill="{ORANGE if i == 2 else "none"}" fill-opacity=".8" stroke="{ORANGE}"/>')
    b.append(f'<path d="M408 250 H426 M474 250 H492" stroke="{DIM}"/>')
    b.append(text(392, 232, 'PILOT', DIM) + text(532, 232, 'FLEET', FG, anchor='end'))
    return svg('dp', '\n'.join(b), 'Edge compute module running Open Loop Autonomy, deployed to a drone, a ground robot and an AMR, scaling from pilot to fleet')


CARDS = [
    ('Hardware', 'Sub-terahertz radar', hardware, [
        'High-resolution sub-THz radar that operates in smoke, fog, dust and darkness, where cameras and LiDAR fail.',
        'It delivers high range and spatial resolution in a compact, low-SWaP-C package built for industrial, robotics and defense environments.']),
    ('Software', 'Open Loop Autonomy', software, [
        'Our autonomy framework navigates, tracks and completes missions using onboard sensing and compute alone: no GPS, no pre-built maps, no continuous communication.',
        'Because it is observation-centric, it keeps working in GPS-denied and contested environments and holds the mission through communication loss. It reduces the need for constant human control while still supporting supervision, and deploys as a software upgrade to existing systems.']),
    ('Machine learning', 'Sensor fusion and perception', ml, [
        'Machine learning turns raw radar and camera data into a real-time understanding of the environment, more robust than any single sensor alone.',
        'Edge-optimized models run object detection and tracking with low latency, and keep perception accurate when visibility drops.']),
    ('Deployment', 'Built to integrate', deployment, [
        'The platform runs in real time on edge devices such as NVIDIA Jetson and integrates with existing robotics and autonomy stacks.',
        'Deploy it as a module or a full system, add capability through software upgrades to Open Loop Autonomy, and scale from a pilot to a fleet-wide rollout.']),
]


def build():
    out = ['<!-- LAYERS:START (generated by tools/platform_diagrams.py) -->', '<div class="layers">']
    for label, title, fn, paras in CARDS:
        body = ''.join(f'<p>{x}</p>' for x in paras)
        out.append(f'''<article class="layer reveal">
  <div class="diag">{fn()}</div>
  <div class="layer-body"><span class="layer-label">{label}</span><h3>{title}</h3>{body}</div>
</article>''')
    out += ['</div>', '<!-- LAYERS:END -->']
    return '\n'.join(out)


if __name__ == '__main__':
    p = Path(__file__).resolve().parent.parent / 'index.html'
    h = p.read_text()
    a, b = h.index('<!-- LAYERS:START'), h.index('<!-- LAYERS:END -->') + len('<!-- LAYERS:END -->')
    p.write_text(h[:a] + build() + h[b:])
    print('diagrams written')
