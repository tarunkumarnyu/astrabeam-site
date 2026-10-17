// Astrabeam site behaviour. Each block guards for its own elements.

// ---------- POV flight video: load and play only while on screen ----------
(() => {
  const video = document.getElementById('pov-video');
  if (!video) return;
  const btn = document.querySelector('.pov-toggle');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let userPaused = reduced;
  const setLabel = () => {
    btn.textContent = video.paused ? 'Play' : 'Pause';
    btn.setAttribute('aria-label', (video.paused ? 'Play' : 'Pause') + ' flight replay');
  };
  btn.addEventListener('click', () => {
    if (video.paused) { userPaused = false; video.play().catch(() => {}); }
    else { userPaused = true; video.pause(); }
  });
  video.addEventListener('play', setLabel);
  video.addEventListener('pause', setLabel);
  setLabel();
  new IntersectionObserver(([e]) => {
    if (e.isIntersecting && !userPaused) video.play().catch(() => {});
    else if (!e.isIntersecting) video.pause();
  }, { threshold: 0.35 }).observe(video);
})();

// ---------- HERO video ----------
(() => {
  const video = document.querySelector('.hero-video');
  const btn = document.querySelector('.video-toggle');
  if (!video || !btn) return;
  const setLabel = () => {
    btn.textContent = video.paused ? 'Play' : 'Pause';
    btn.setAttribute('aria-label', (video.paused ? 'Play' : 'Pause') + ' background video');
  };
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) { video.removeAttribute('autoplay'); video.pause(); }
  btn.addEventListener('click', () => { video.paused ? video.play() : video.pause(); });
  video.addEventListener('play', setLabel);
  video.addEventListener('pause', setLabel);
  setLabel();
})();

// ---------- NAV state ----------
const nav = document.querySelector('.nav');
window.addEventListener('scroll', () => nav.classList.toggle('scrolled', scrollY > 40));

// ---------- Reveal on scroll ----------
const io = new IntersectionObserver((entries) => {
  entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
}, { threshold: 0.15 });
document.querySelectorAll('.reveal').forEach((el, i) => { el.style.transitionDelay = (i % 4) * 80 + 'ms'; io.observe(el); });

// ---------- Phone menu ----------
(() => {
  const btn = document.querySelector('.nav-toggle');
  const menu = document.getElementById('site-nav');
  if (!btn || !menu) return;
  const set = (open) => {
    menu.classList.toggle('open', open);
    btn.setAttribute('aria-expanded', open);
    btn.textContent = open ? 'Close' : 'Menu';
  };
  btn.addEventListener('click', () => set(!menu.classList.contains('open')));
  menu.querySelectorAll('a').forEach((a) => a.addEventListener('click', () => set(false)));
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') set(false); });
})();

// ---------- Contact form preview (on Squarespace a native Form Block replaces it) ----------
(() => {
  const form = document.getElementById('contact-form');
  if (!form) return;
  const note = document.getElementById('form-note');
  // grey "Select…" placeholder until an option is chosen
  const sel = form.querySelector('select');
  const syncSel = () => sel.classList.toggle('is-empty', !sel.value);
  sel.addEventListener('change', syncSel); syncSel();
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    let firstBad = null;
    for (const el of form.querySelectorAll('[required]')) {
      const v = el.value.trim();
      const ok = v && (el.type !== 'email' || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v));
      el.setAttribute('aria-invalid', ok ? 'false' : 'true');
      if (!ok && !firstBad) firstBad = el;
    }
    if (firstBad) { note.textContent = 'Please fill in your name, a valid email and a short message.'; firstBad.focus(); return; }
    note.textContent = 'Preview only: on the live site this form sends to info@astrabeam.com.';
  });
})();

// ---------- Platform diagrams: SMIL animations pause for reduced motion and off-screen ----------
(() => {
  const svgs = document.querySelectorAll('.diag-svg');
  if (!svgs.length) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  svgs.forEach((s) => s.pauseAnimations && s.pauseAnimations());
  if (reduced) return;
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => e.isIntersecting ? e.target.unpauseAnimations() : e.target.pauseAnimations());
  });
  svgs.forEach((s) => io.observe(s));
})();
