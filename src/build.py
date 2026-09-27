import json, os
S = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(S, "guiones.json"), encoding="utf-8"))
tpl = r'''<title>Teleprompter EM360</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&display=swap">
<style>
:root{--bg:#0b0b0d;--panel:#16161a;--line:#2a2a30;--fg:#f3f1ec;--dim:#9a978f;--acc:#e0b04a;--accfg:#1a1408;--gancho:#ffd36a;--btn:#26262c;--btnfg:#f3f1ec;color-scheme:dark}
html,body{height:100%}
body{margin:0;background:var(--bg);color:var(--fg);font-family:"Atkinson Hyperlegible",system-ui,-apple-system,"Segoe UI",sans-serif;overflow:hidden;-webkit-user-select:none;user-select:none}
#app{display:flex;flex-direction:column;height:100%}
header{display:flex;align-items:center;gap:6px;padding:4px 8px;padding-top:calc(4px + env(safe-area-inset-top,0px));background:var(--panel);border-bottom:1px solid var(--line);flex:0 0 auto}
header button{flex:0 0 auto}
#sel{flex:1 1 auto;min-width:0;background:var(--btn);color:var(--btnfg);border:1px solid var(--line);border-radius:6px;padding:5px 6px;font:inherit;font-size:12px;height:26px}
button{background:var(--btn);color:var(--btnfg);border:1px solid var(--line);border-radius:6px;font:inherit;font-weight:700;font-size:13px;padding:0 6px;height:26px;min-width:26px;cursor:pointer;touch-action:manipulation;line-height:1}
button:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
button.on{background:var(--acc);color:var(--accfg);border-color:var(--acc)}
#stage{flex:1 1 auto;position:relative;overflow:hidden}
#scroll{position:absolute;inset:0;overflow-y:auto;overflow-x:hidden;scrollbar-width:none;-webkit-overflow-scrolling:touch}
#scroll::-webkit-scrollbar{display:none}
#text{padding:42vh 20px 60vh;max-width:820px;margin:0 auto;font-size:var(--fs,34px);line-height:1.35;font-weight:700;text-wrap:pretty}
#text.mirror{transform:scaleX(-1)}
#text .meta{font-size:.5em;font-weight:400;color:var(--dim);line-height:1.3;margin-bottom:.6em}
#text .cifras{font-size:.55em;font-weight:400;color:var(--acc);line-height:1.35;margin-bottom:1.2em;border-left:3px solid var(--acc);padding-left:.6em}
#text .cifras span{display:block}
#text .gancho{color:var(--gancho);margin:0 0 .9em}
#text .lbl{display:block;font-size:.42em;font-weight:400;letter-spacing:.12em;text-transform:uppercase;color:var(--dim);margin:1.1em 0 .25em}
#text p{margin:0 0 .7em;white-space:pre-line}
#text .fin{color:var(--dim);font-size:.6em;font-weight:400;margin-top:2em;text-align:center}
#line{position:absolute;left:0;right:0;top:42vh;height:0;border-top:2px solid var(--acc);opacity:.55;pointer-events:none}
#line::before{content:"";position:absolute;left:6px;top:-7px;border:6px solid transparent;border-left:9px solid var(--acc)}
footer{flex:0 0 auto;background:var(--panel);border-top:1px solid var(--line);padding:4px 8px;padding-bottom:calc(4px + env(safe-area-inset-bottom,0px));display:flex;align-items:center;gap:4px;overflow-x:auto;scrollbar-width:none}
footer::-webkit-scrollbar{display:none}
.grp{display:flex;align-items:center;gap:2px;flex:0 0 auto}
.grp .lab{display:none}
.grp .val{font-size:11px;color:var(--dim);min-width:24px;text-align:center;font-variant-numeric:tabular-nums}
#play{flex:0 0 auto;min-width:36px}
.sep{flex:1 1 auto}
.nav{display:flex;gap:4px;flex:0 0 auto}
@media (max-width:420px){#text{padding-left:16px;padding-right:16px}}
</style>
<div id="app">
<header>
<button id="prev" aria-label="Guion anterior">&#9664;</button>
<select id="sel" aria-label="Elegir guion"></select>
<button id="next" aria-label="Guion siguiente">&#9654;</button>
</header>
<div id="stage">
<div id="scroll"><div id="text"></div></div>
<div id="line"></div>
</div>
<footer>
<button id="play" aria-label="Empezar o pausar">&#9654;</button>
<div class="grp"><span class="lab">Vel.</span><button id="vm" aria-label="Menos velocidad">&minus;</button><span class="val" id="vv">1,0</span><button id="vp" aria-label="Más velocidad">+</button></div>
<div class="grp"><span class="lab">Letra</span><button id="fm" aria-label="Letra más pequeña">A&minus;</button><span class="val" id="fv">34</span><button id="fp" aria-label="Letra más grande">A+</button></div>
<span class="sep"></span>
<div class="nav"><button id="top" aria-label="Al inicio">&#8679;</button><button id="mirror" aria-label="Espejo">&#8644;</button><button id="cif" aria-label="Mostrar u ocultar cifras">#</button></div>
</footer>
</div>
<script>
const G = __DATA__;
const $ = id => document.getElementById(id);
const scroll = $("scroll"), text = $("text");
let cur = 0, playing = false, speed = 1.0, fs = 34, mirror = false, showCif = true, raf = null, last = 0, acc = 0;
const load = (k, d) => { try { const v = localStorage.getItem("tp_" + k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } };
const save = (k, v) => { try { localStorage.setItem("tp_" + k, JSON.stringify(v)); } catch (e) {} };
speed = load("speed", 1.0); fs = load("fs", 34); mirror = load("mirror", false); showCif = load("cif", true); cur = Math.min(load("cur", 0), G.length - 1);
const esc = s => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
function fillSel() {
  let g = null, html = "";
  G.forEach((s, i) => { if (s.grupo !== g) { if (g) html += "</optgroup>"; g = s.grupo; html += '<optgroup label="' + esc(g) + '">'; } html += '<option value="' + i + '">' + esc(s.id + " · " + s.title) + "</option>"; });
  html += "</optgroup>"; $("sel").innerHTML = html;
}
function render() {
  const s = G[cur]; let h = "";
  h += '<div class="meta">' + esc(s.id + " · " + s.title) + (s.meta.length ? "<br>" + esc(s.meta.join(" · ")) : "") + (s.nota ? "<br>Rodaje: " + esc(s.nota) : "") + "</div>";
  if (showCif && s.cifras.length) h += '<div class="cifras">' + s.cifras.map(c => "<span>" + esc(c) + "</span>").join("") + "</div>";
  if (s.gancho) h += '<span class="lbl">Gancho</span><p class="gancho">' + esc(s.gancho) + "</p>";
  s.blocks.forEach(b => { h += '<span class="lbl">' + esc((b.t ? b.t + " · " : "") + b.b) + "</span><p>" + esc(b.x) + "</p>"; });
  h += '<p class="fin">Fin · ' + esc(s.id) + "</p>";
  text.innerHTML = h; text.style.setProperty("--fs", fs + "px"); text.classList.toggle("mirror", mirror);
  $("sel").value = cur; scroll.scrollTop = 0; save("cur", cur);
  $("vv").textContent = speed.toFixed(1).replace(".", ","); $("fv").textContent = fs;
  $("mirror").classList.toggle("on", mirror); $("cif").classList.toggle("on", showCif);
}
function step(ts) {
  if (!playing) return;
  if (last) { acc += (ts - last) / 1000 * speed * 55; const px = Math.floor(acc); if (px) { scroll.scrollTop += px; acc -= px; } }
  last = ts;
  if (scroll.scrollTop + scroll.clientHeight >= scroll.scrollHeight - 2) { setPlay(false); return; }
  raf = requestAnimationFrame(step);
}
function setPlay(p) { playing = p; last = 0; acc = 0; $("play").classList.toggle("on", p); $("play").innerHTML = p ? "&#10074;&#10074;" : "&#9654;"; if (p) raf = requestAnimationFrame(step); else if (raf) cancelAnimationFrame(raf); }
function go(i) { setPlay(false); cur = (i + G.length) % G.length; render(); }
$("play").onclick = () => setPlay(!playing);
scroll.addEventListener("click", () => setPlay(!playing));
$("vm").onclick = () => { speed = Math.max(0.2, +(speed - 0.1).toFixed(1)); save("speed", speed); $("vv").textContent = speed.toFixed(1).replace(".", ","); };
$("vp").onclick = () => { speed = Math.min(4, +(speed + 0.1).toFixed(1)); save("speed", speed); $("vv").textContent = speed.toFixed(1).replace(".", ","); };
$("fm").onclick = () => { fs = Math.max(18, fs - 2); save("fs", fs); text.style.setProperty("--fs", fs + "px"); $("fv").textContent = fs; };
$("fp").onclick = () => { fs = Math.min(72, fs + 2); save("fs", fs); text.style.setProperty("--fs", fs + "px"); $("fv").textContent = fs; };
$("top").onclick = () => { setPlay(false); scroll.scrollTop = 0; };
$("mirror").onclick = () => { mirror = !mirror; save("mirror", mirror); text.classList.toggle("mirror", mirror); $("mirror").classList.toggle("on", mirror); };
$("cif").onclick = () => { showCif = !showCif; save("cif", showCif); render(); };
$("prev").onclick = () => go(cur - 1); $("next").onclick = () => go(cur + 1);
$("sel").onchange = e => go(+e.target.value);
document.addEventListener("keydown", e => { if (e.code === "Space") { e.preventDefault(); setPlay(!playing); } if (e.key === "ArrowRight") go(cur + 1); if (e.key === "ArrowLeft") go(cur - 1); if (e.key === "ArrowUp") $("vp").click(); if (e.key === "ArrowDown") $("vm").click(); });
let wl = null; async function lock() { try { if (navigator.wakeLock && !wl) { wl = await navigator.wakeLock.request("screen"); wl.addEventListener("release", () => { wl = null; }); } } catch (e) {} }
document.addEventListener("click", lock, { once: true }); document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible") lock(); });
fillSel(); render();
</script>'''
html = tpl.replace("__DATA__", json.dumps(data, ensure_ascii=False))
open(os.path.join(S, "teleprompter-em360.html"), "w", encoding="utf-8").write(html)
print(len(html))
