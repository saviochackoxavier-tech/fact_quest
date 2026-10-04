const FX = {
  csrf: () => document.querySelector('meta[name=csrf]').content,
  async api(url, body) {
    const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': FX.csrf() }, body: JSON.stringify(body) });
    const data = await r.json();
    if (!r.ok) throw new Error(data.error || 'Request failed');
    return data;
  },
  setBar(id, pct, color) {
    const el = document.querySelector(`#${id} > i`);
    if (!el) return;
    el.style.width = Math.max(0, Math.min(100, pct)) + '%';
    if (color) el.style.background = color;
    else el.style.background = pct > 50 ? '#10b981' : pct > 25 ? '#f59e0b' : '#ef4444';
  },
  floatText(text, anchor, color = '#34d399') {
    const r = (anchor || document.body).getBoundingClientRect();
    const d = document.createElement('div');
    d.className = 'float-text'; d.textContent = text; d.style.color = color;
    d.style.left = (r.left + r.width / 2 - 30) + 'px'; d.style.top = (r.top + 10) + 'px';
    document.body.appendChild(d); setTimeout(() => d.remove(), 1300);
  },
  flash(color = '#10b981') {
    const d = document.createElement('div'); d.className = 'flash'; d.style.background = color;
    document.body.appendChild(d); setTimeout(() => d.remove(), 400);
  },
  shake(el) { el.classList.remove('shake'); void el.offsetWidth; el.classList.add('shake'); },
  beep(freq = 440, ms = 90) {
    try {
      const c = FX._ctx || (FX._ctx = new (window.AudioContext || window.webkitAudioContext)());
      const o = c.createOscillator(), g = c.createGain();
      o.type = 'square'; o.frequency.value = freq; g.gain.value = 0.04;
      o.connect(g); g.connect(c.destination); o.start(); o.stop(c.currentTime + ms / 1000);
    } catch (e) {}
  },
  loading(el, msg = '> CONSULTING THE ORACLE... [SERPAPI LINK ESTABLISHED]') {
    el.innerHTML = `<span class="text-amber-300">${msg}</span><span class="blink">_</span>`;
  },
  hud(p) {
    document.getElementById('hud-name').textContent = p.name;
    document.getElementById('hud-level').textContent = p.level;
    document.getElementById('hud-hp').textContent = p.hp;
    document.getElementById('hud-xp').textContent = p.xp;
    FX.setBar('hud-hpbar', p.hp);
    FX.setBar('hud-xpbar', p.xp_pct, '#38bdf8');
  },
  esc: s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])),
  safeUrl: u => /^https?:\/\//i.test(u) ? u : '#',
};
document.addEventListener('DOMContentLoaded', () => {
  const hp = document.getElementById('hud-hp');
  if (hp) { FX.setBar('hud-hpbar', +hp.textContent); FX.setBar('hud-xpbar', +document.getElementById('hud-xpbar').dataset.pct, '#38bdf8'); }
});
