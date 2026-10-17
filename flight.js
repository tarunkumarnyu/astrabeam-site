// Flight replay: recorded flight -> synced camera video + 3D view.
// Data is robot-centred: x forward, y left, z up.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const $ = (id) => document.getElementById(id);
const video = $('fl-video');
const canvas = $('fl-canvas');
const scrub = $('fl-scrub');
const playBtn = $('fl-play');

const RED = 0xff4d3d, GREEN = 0x3dffa8, BLUE = 0x4da3ff, ORANGE = 0xff6600;
const MAX_OBS = 10, MAX_PATH = 10;

// FLU body frame -> three.js (x right, y up, z towards viewer)
const toThree = (p, out = new THREE.Vector3()) => out.set(-p[1], p[2], -p[0]);

// a page can point the replay at another recording: <section id="flight" data-flight="…/flight.json">
const dataUrl = document.getElementById('flight')?.dataset.flight || 'assets/flight/flight.json';
const data = await fetch(dataUrl).then((r) => r.json());
const { meta, samples } = data;
const N = samples.length, HZ = meta.hz;
const R = meta.obstacle_radius;
scrub.max = N - 1;

// ---------- three.js scene ----------
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0x050608, 10, 22);
const camera = new THREE.PerspectiveCamera(45, 1, 0.05, 100);
camera.position.set(3.2, 3.4, 4.6);
const controls = new OrbitControls(camera, canvas);
controls.target.set(0, 0.4, -3.5);
controls.enableDamping = true;
controls.enablePan = false;
controls.minDistance = 3;
controls.maxDistance = 16;
controls.maxPolarAngle = Math.PI * 0.49;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.35;
canvas.addEventListener('pointerdown', () => (controls.autoRotate = false));

// ground grid: sits at -height in the body frame, so it drops away as the drone climbs
const grid = new THREE.GridHelper(24, 24, 0x2a3038, 0x161a1f);
grid.position.z = -6;
scene.add(grid);

// range rings on the ground, every 2 m ahead of the robot
const rings = new THREE.Group();
for (let r = 2; r <= 12; r += 2) {
  const pts = [];
  for (let a = -Math.PI / 2.4; a <= Math.PI / 2.4; a += 0.05) pts.push(new THREE.Vector3(Math.sin(a) * r, 0, -Math.cos(a) * r));
  rings.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({ color: 0x3dffa8, transparent: true, opacity: 0.12 })));
}
scene.add(rings);

// robot: a small quad "X" at the origin
const robot = new THREE.Group();
const armMat = new THREE.MeshBasicMaterial({ color: 0xeceef1 });
for (const ang of [Math.PI / 4, -Math.PI / 4]) {
  const arm = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.025, 0.04), armMat);
  arm.rotation.y = ang;
  robot.add(arm);
}
for (const [x, z] of [[0.14, 0.14], [-0.14, 0.14], [0.14, -0.14], [-0.14, -0.14]]) {
  const rotor = new THREE.Mesh(new THREE.TorusGeometry(0.065, 0.007, 6, 24), new THREE.MeshBasicMaterial({ color: ORANGE }));
  rotor.rotation.x = Math.PI / 2;
  rotor.position.set(x, 0.02, z);
  robot.add(rotor);
}
// heading tick (forward = -z)
robot.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, 0, -0.08), new THREE.Vector3(0, 0, -0.3)]), new THREE.LineBasicMaterial({ color: ORANGE })));
// altitude stalk down to the ground
const stalkGeo = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3(0, -1, 0)]);
const stalk = new THREE.Line(stalkGeo, new THREE.LineDashedMaterial({ color: 0x7c838d, dashSize: 0.08, gapSize: 0.08 }));
robot.add(stalk);
scene.add(robot);

// safety zones (pooled)
const sphereGeo = new THREE.SphereGeometry(R, 20, 14);
const spheres = [];
for (let i = 0; i < MAX_OBS; i++) {
  const g = new THREE.Group();
  g.add(new THREE.Mesh(sphereGeo, new THREE.MeshBasicMaterial({ color: RED, transparent: true, opacity: 0.07, depthWrite: false })));
  g.add(new THREE.LineSegments(new THREE.WireframeGeometry(sphereGeo), new THREE.LineBasicMaterial({ color: RED, transparent: true, opacity: 0.35 })));
  g.add(new THREE.Mesh(new THREE.SphereGeometry(0.05, 8, 6), new THREE.MeshBasicMaterial({ color: RED })));
  g.visible = false;
  scene.add(g);
  spheres.push(g);
}

// target and planned paths
// Paths draw on top of everything (short local plans would otherwise hide under the drone).
function pathLine(color) {
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(MAX_PATH * 3), 3));
  const line = new THREE.Line(geo, new THREE.LineBasicMaterial({ color, depthTest: false }));
  const dots = new THREE.Points(geo, new THREE.PointsMaterial({ color, size: 0.06, depthTest: false }));
  const tubeMat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.9, depthTest: false });
  const tube = new THREE.Mesh(new THREE.BufferGeometry(), tubeMat);
  const tip = new THREE.Mesh(new THREE.SphereGeometry(0.035, 10, 8), tubeMat);
  for (const o of [line, dots, tube, tip]) o.renderOrder = 10;
  scene.add(line, dots, tube, tip);
  return { geo, line, dots, tube, tip };
}
const refLine = pathLine(GREEN);
const predLine = pathLine(BLUE);

function setPath(path, pts) {
  const arr = path.geo.attributes.position.array;
  const v = new THREE.Vector3();
  pts.slice(0, MAX_PATH).forEach((p, i) => { toThree(p, v); arr[i * 3] = v.x; arr[i * 3 + 1] = v.y; arr[i * 3 + 2] = v.z; });
  path.geo.attributes.position.needsUpdate = true;
  const n = Math.min(pts.length, MAX_PATH);
  path.geo.setDrawRange(0, n);
  path.tube.geometry.dispose();
  path.tip.visible = n > 0;
  const span = n >= 2 ? Math.hypot(...pts[n - 1].map((v, k) => v - pts[0][k])) : 0;
  if (n >= 2 && span > 0.01) {
    const curve = new THREE.CatmullRomCurve3(pts.slice(0, n).map((p) => toThree(p)));
    path.tube.geometry = new THREE.TubeGeometry(curve, 24, 0.012, 6, false);
    path.tip.position.copy(toThree(pts[n - 1]));
  } else {
    path.tube.geometry = new THREE.BufferGeometry();
  }
}

function resize() {
  const w = canvas.clientWidth, h = canvas.clientHeight;
  if (!w || !h) return;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(canvas);

// ---------- timeline band: autonomy + obstacle presence ----------
function drawBand() {
  const band = $('fl-band');
  const w = band.clientWidth, h = band.clientHeight;
  band.width = w * devicePixelRatio; band.height = h * devicePixelRatio;
  const c = band.getContext('2d');
  c.scale(devicePixelRatio, devicePixelRatio);
  c.fillStyle = '#14171c'; c.fillRect(0, 0, w, h);
  const cw = w / N;
  samples.forEach((s, i) => {
    if (s.mode === 'AUTO') { c.fillStyle = 'rgba(61,255,168,.55)'; c.fillRect(i * cw, 0, cw + 0.5, h * 0.55); }
    if (s.obs.length) { c.fillStyle = 'rgba(255,77,61,.8)'; c.fillRect(i * cw, h * 0.7, cw + 0.5, h * 0.3); }
  });
}
new ResizeObserver(drawBand).observe($('fl-band'));

// ---------- per-sample update ----------
const fmt = (v, d = 1) => (v === null || v === undefined ? '–' : v.toFixed(d));
const modeEl = $('fl-mode');
let current = -1;

function show(i) {
  if (i === current) return;
  current = i;
  const s = samples[i];
  const v = new THREE.Vector3();
  spheres.forEach((g, k) => {
    const p = s.obs[k];
    g.visible = !!p;
    if (p) g.position.copy(toThree(p, v));
  });
  setPath(refLine, s.ref);
  setPath(predLine, s.pred);
  const alt = Math.max(0, s.alt ?? 0);
  grid.position.y = rings.position.y = -alt;
  stalk.scale.y = Math.max(alt, 0.001);
  stalk.computeLineDistances();

  $('st-speed').textContent = fmt(s.speed);
  $('st-alt').textContent = fmt(s.alt);
  $('st-near').textContent = fmt(s.near);
  $('st-obs').textContent = s.obs.length;
  const on = s.mode === 'AUTO';
  if (modeEl) {
    modeEl.textContent = on ? 'AUTONOMOUS' : s.mode === 'MANUAL' ? 'MANUAL' : 'MODE UNCONFIRMED';
    modeEl.classList.toggle('on', on);
  }
  scrub.value = i;
  $('fl-time').textContent = `${s.t.toFixed(1).padStart(4, '0')} / ${meta.duration.toFixed(1)} s`;
}

// ---------- playback ----------
const indexAt = (t) => Math.min(N - 1, Math.max(0, Math.floor(t * HZ + 1e-3)));
let visible = false;

function tick() {
  requestAnimationFrame(tick);
  if (!visible) return;
  try { show(indexAt(video.currentTime)); } catch (err) { console.warn('replay sample skipped', err); }
  controls.update();
  renderer.render(scene, camera);
}

const setPlayLabel = () => {
  playBtn.textContent = video.paused ? '▶' : '❚❚';
  playBtn.setAttribute('aria-label', video.paused ? 'Play replay' : 'Pause replay');
};
playBtn.addEventListener('click', () => (video.paused ? video.play() : video.pause()));
video.addEventListener('play', setPlayLabel);
video.addEventListener('pause', setPlayLabel);
video.addEventListener('ended', () => { video.currentTime = 0; video.play(); });
scrub.addEventListener('input', () => {
  video.pause();
  video.currentTime = (+scrub.value + 0.5) / HZ;
  show(+scrub.value);
});

const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
if (reduced) controls.autoRotate = false;
let userPaused = false;
playBtn.addEventListener('click', () => (userPaused = video.paused));

new IntersectionObserver(([e]) => {
  visible = e.isIntersecting;
  if (visible && !reduced && !userPaused) video.play().catch(() => {});
  if (!visible) video.pause();
}, { threshold: 0.25 }).observe($('fl-canvas').closest('.fl-grid'));

resize();
try { show(0); } catch (err) { console.warn('replay first sample skipped', err); }
renderer.render(scene, camera);
tick();
