// Records the live Pharmakon site for the pitch film's walkthrough (scene "demo").
//
// Capture: Chrome CDP screencast at deviceScaleFactor 2 (3840x2160 JPEG frames) on the real GPU (ANGLE/EGL),
// assembled into CFR 30 fps H.264 (yuv420p, crf 18). Headless Chrome paints 4K at only ~18 fps, so every page
// scroll is performed SLOW times slower than it should play and is re-timed by 1/SLOW at encode time (a time warp
// applied identically to the frames and to the action log), giving scrolls ~45 unique frames/s.
//
// Every action runs on a fixed schedule (seconds of clip time, matched to the VO in video/film/src/timing.ts) and
// is logged in clip time (CSS px of the 1920x1080 viewport) to video/film/public/rec/actions.json. The real cursor
// is never drawn (headless); the film draws its own from this log.
// Usage: node video/rec/record.cjs [clip ...]   (default: all clips)
const { chromium } = require("/home/arpit/.npm/_npx/9833c18b2d85bc59/node_modules/playwright");
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const SITE = "https://pharmakon.adoranto737.workers.dev";
const OUT = path.resolve(__dirname, "../film/public/rec");
const FRAMES = path.resolve(__dirname, "frames");
const UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36";
const W = 1920, H = 1080, FPS = 30;
const SLOW = 2.5; // scroll slow-motion factor during capture
fs.mkdirSync(OUT, { recursive: true });

const ACTIONS_FILE = path.join(OUT, "actions.json");
const log = fs.existsSync(ACTIONS_FILE) ? JSON.parse(fs.readFileSync(ACTIONS_FILE, "utf8")) : { clips: {} };
Object.assign(log, { viewport: { w: W, h: H }, fps: FPS, note: "times in clip seconds (natural speed); x/y/w/h in CSS px of the 1920x1080 viewport" });
const now = () => Date.now() / 1000;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const easeInOut = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

// ---------------------------------------------------------------- clip recorder
const PENDING = []; // encodes run after the browser closes, so capture never competes with ffmpeg
let rec = null;
async function startClip(name, page, cursor = { x: W / 2, y: H * 0.62 }) {
  await page.waitForLoadState("networkidle", { timeout: 20000 }).catch(() => console.log("  (network not idle after 20 s, starting anyway)"));
  const dir = path.join(FRAMES, name);
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(dir, { recursive: true });
  const cdp = await page.context().newCDPSession(page);
  const r = { name, page, cdp, dir, frames: [], actions: [], cursor: { ...cursor }, t0: now(), warps: [] };
  cdp.on("Page.screencastFrame", (f) => {
    cdp.send("Page.screencastFrameAck", { sessionId: f.sessionId }).catch(() => {});
    const file = `f${String(r.frames.length).padStart(5, "0")}.jpg`;
    r.frames.push({ ts: f.metadata.timestamp, file });
    fs.writeFile(path.join(dir, file), Buffer.from(f.data, "base64"), () => {});
  });
  await cdp.send("Page.startScreencast", { format: "jpeg", quality: 85, maxWidth: W * 2, maxHeight: H * 2 });
  await page.evaluate(() => window.scrollBy(0, 0));
  r.t0 = now();
  rec = r;
  act("cursor", { x: cursor.x, y: cursor.y });
  return r;
}

/** real seconds since clip start -> clip time (natural seconds): slow scroll windows count 1/SLOW */
const natural = (r, real) => real - r.warps.reduce((acc, [a, b]) => acc + Math.max(0, Math.min(real, b ?? real) - a) * (1 - 1 / SLOW), 0);
const ct = () => natural(rec, now() - rec.t0);
function act(type, data = {}) {
  const a = { t: +ct().toFixed(3), type, ...data };
  rec.actions.push(a);
  return a;
}
const mark = (name) => { console.log(`  [${rec.name}] ${name} @${ct().toFixed(2)}s (real ${((now() - rec.t0)).toFixed(1)}s)`); return act("mark", { name }); };
/** wait until clip time reaches `sec` (the schedule) */
async function at(sec) {
  const late = ct() - sec;
  if (late > 0.15) console.log(`  [${rec.name}] ${late.toFixed(2)} s late for t=${sec}`);
  while (ct() < sec) await sleep(Math.min(40, (sec - ct()) * 1000));
}
const wait = (ms) => sleep(ms);

async function stopClip() {
  const r = rec;
  const tEnd = now();
  await r.cdp.send("Page.stopScreencast").catch(() => {});
  await sleep(300);
  await r.cdp.detach().catch(() => {});
  const N = (ts) => natural(r, Math.max(0, ts - r.t0));
  const dur = N(tEnd);
  const fr = r.frames.filter((f, i) => i === 0 || f.ts > r.frames[i - 1].ts);
  const lines = [];
  fr.forEach((f, i) => {
    const start = i === 0 ? r.t0 : Math.max(f.ts, r.t0);
    const end = i + 1 < fr.length ? Math.max(fr[i + 1].ts, r.t0) : tEnd;
    lines.push(`file '${f.file}'`, `duration ${Math.max(0.0005, N(end) - N(start)).toFixed(5)}`);
  });
  lines.push(`file '${fr[fr.length - 1].file}'`);
  fs.writeFileSync(path.join(r.dir, "list.txt"), lines.join("\n"));
  // smoothness check: effective frame rate and largest gap (natural time) inside every scroll
  const gaps = r.actions.filter((a) => a.type === "scroll").map((a) => {
    const ts = [a.t, ...fr.map((f) => N(f.ts)).filter((x) => x > a.t && x < a.t + a.dur), a.t + a.dur];
    let g = 0; for (let i = 1; i < ts.length; i++) g = Math.max(g, ts[i] - ts[i - 1]);
    return { t: a.t, fps: +((ts.length - 2) / a.dur).toFixed(1), maxGapMs: Math.round(g * 1000) };
  });
  console.log(`[${r.name}] scroll smoothness ${JSON.stringify(gaps)}`);
  const mp4 = path.join(OUT, `${r.name}.mp4`);
  PENDING.push(() => execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", path.join(r.dir, "list.txt"),
    "-vf", `fps=${FPS},scale=${W * 2}:${H * 2}:flags=lanczos,format=yuv420p`, "-c:v", "libx264", "-preset", "medium", "-crf", "18",
    "-g", "15", "-movflags", "+faststart", "-an", mp4]));
  log.clips[r.name] = { file: `rec/${r.name}.mp4`, duration: +dur.toFixed(3), frames: fr.length, recordedAt: new Date().toISOString(), url: r.page.url(), scrollSlowMotionCapture: SLOW, actions: r.actions };
  fs.writeFileSync(ACTIONS_FILE, JSON.stringify(log, null, 1));
  console.log(`[${r.name}] ${dur.toFixed(1)} s (natural), ${fr.length} frames (${(fr.length / dur).toFixed(1)}/s) -> ${mp4}`);
  rec = null;
}

// ---------------------------------------------------------------- humane input (all durations in natural ms)
async function moveTo(x, y, ms = 700) {
  const p = rec.page, from = { ...rec.cursor };
  act("move", { x: Math.round(x), y: Math.round(y), dur: ms / 1000 });
  const steps = Math.max(8, Math.round(ms / 40));
  const t0 = now();
  for (let i = 1; i <= steps; i++) {
    const k = easeInOut(i / steps);
    await p.mouse.move(from.x + (x - from.x) * k, from.y + (y - from.y) * k);
    const due = t0 + (ms / 1000) * (i / steps) - now(); // keep to the schedule whatever each move costs
    if (due > 0) await sleep(due * 1000);
  }
  rec.cursor = { x, y };
}
async function box(sel, nth = 0) {
  const b = await rec.page.locator(sel).nth(nth).boundingBox();
  if (!b) throw new Error(`no box for ${sel}`);
  return b;
}
async function moveToEl(sel, ms = 700, fx = 0.5, fy = 0.5, nth = 0) {
  const b = await box(sel, nth);
  await moveTo(b.x + b.width * fx, b.y + b.height * fy, ms);
  return b;
}
async function click(label) {
  act("click", { x: Math.round(rec.cursor.x), y: Math.round(rec.cursor.y), label });
  await rec.page.mouse.down();
  await wait(80);
  await rec.page.mouse.up();
}
async function typeText(text, sel) {
  const delays = [120, 95, 140, 85, 110, 150, 90, 125, 100, 135, 115, 105];
  act("type", { text, dur: delays.slice(0, text.length).reduce((a, b) => a + b, 0) / 1000 });
  for (let i = 0; i < text.length; i++) {
    await rec.page.locator(sel).pressSequentially(text[i]);
    await wait(delays[i % delays.length]);
  }
}
async function focus(sel, label, nth = 0, pad = 16) {
  const b = await box(sel, nth);
  act("focus", { x: Math.round(b.x - pad), y: Math.round(b.y - pad), w: Math.round(b.width + 2 * pad), h: Math.round(b.height + 2 * pad), label });
  return b;
}
const focusBox = (b, label, pad = 12) => act("focus", { x: Math.round(b.x - pad), y: Math.round(b.y - pad), w: Math.round(b.width + 2 * pad), h: Math.round(b.height + 2 * pad), label });
const docY = (sel) => rec.page.evaluate((s) => document.querySelector(s).getBoundingClientRect().top + scrollY, sel);
/** eased page scroll lasting `ms` in the film: performed SLOW times slower, re-timed at encode */
async function scrollTo(y, ms = 1400) {
  const from = await rec.page.evaluate(() => scrollY);
  act("scroll", { from: Math.round(from), to: Math.round(y), dur: ms / 1000 });
  const w = [now() - rec.t0, null];
  rec.warps.push(w);
  await rec.page.evaluate(([from, to, ms]) => new Promise((res) => {
    const t0 = performance.now();
    const e = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
    const step = () => { const k = Math.min(1, (performance.now() - t0) / ms); window.scrollTo({ top: from + (to - from) * e(k), behavior: "instant" }); k < 1 ? requestAnimationFrame(step) : res(); };
    requestAnimationFrame(step);
  }), [from, y, ms * SLOW]);
  w[1] = now() - rec.t0;
}
const jump = (page, y) => page.evaluate((y) => window.scrollTo({ top: y, behavior: "instant" }), y);
const allImages = (page, scope = "") => page.evaluate((s) => Promise.all([...document.querySelectorAll(`${s} img`)].map((i) => i.complete ? 0 : new Promise((r) => { i.onload = i.onerror = r; setTimeout(r, 15000); }))), scope);

// ---------------------------------------------------------------- browser setup
const imgCache = new Map();
async function newContext(browser) {
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 2, userAgent: UA, colorScheme: "dark", acceptDownloads: true });
  ctx.setDefaultTimeout(90000);
  ctx.setDefaultNavigationTimeout(90000);
  // Wikimedia photos (the site's real candidate/lead images) are slow through redirects: fetch each once, then
  // serve the same bytes from memory so they appear without loading gaps.
  await ctx.route(/wikimedia\.org/, async (route) => {
    const u = route.request().url();
    try {
      if (!imgCache.has(u)) {
        const r = await route.fetch({ maxRedirects: 10, timeout: 25000 });
        imgCache.set(u, { body: await r.body(), ct: r.headers()["content-type"] || "image/jpeg" });
      }
      const c = imgCache.get(u);
      await route.fulfill({ status: 200, body: c.body, headers: { "content-type": c.ct, "access-control-allow-origin": "*", "cache-control": "max-age=86400" } });
    } catch { await route.continue().catch(() => {}); }
  });
  return ctx;
}

async function warm(page) {
  // load every image the takes will show, so the recording has no loading gaps
  await page.goto(SITE + "/#name=dmm-3-23", { waitUntil: "load" });
  for (let y = 0; y < 12500; y += 500) { await jump(page, y); await sleep(150); }
  await page.selectOption("#lead-cond", "Eye Diseases");
  await page.evaluate(() => { const r = document.getElementById("pmin"); r.value = "0.5"; r.dispatchEvent(new Event("input")); document.getElementById("hide-tox").click(); });
  await page.evaluate(() => document.getElementById("lead-grid").scrollIntoView());
  for (let i = 0; i < 6; i++) { await page.evaluate(() => window.scrollBy(0, 400)); await sleep(200); }
  await allImages(page);
}

async function open(page, hash = "") {
  await page.goto(SITE + "/" + hash, { waitUntil: "load" });
  await page.waitForLoadState("networkidle", { timeout: 20000 }).catch(() => {});
}
const topOf = (page, id) => page.evaluate((id) => document.getElementById(id).getBoundingClientRect().top + scrollY, id);

// ---------------------------------------------------------------- clips (schedules in natural seconds = VO-aligned)
const CLIPS = {
  // scene "demo" frames 0..~1215 (s08_a .. start of s08_e)
  async explorer(page) {
    await open(page);
    const exTop = await topOf(page, "explorer");
    await jump(page, exTop - 560);
    await sleep(1500);
    await allImages(page);
    await startClip("explorer", page, { x: 1240, y: 760 });
    mark("start");
    await at(1.5);
    await scrollTo(exTop, 3000); // land exactly on the section, so the site's own scrollIntoView on open is a no-op
    mark("explorer_in");
    await at(4.75);
    await moveToEl("#q", 800, 0.3, 0.5);
    await at(6.2);
    await click("search");
    mark("type");
    await at(6.45);
    await typeText("apsinthion", "#q");
    await at(8.0);
    await moveToEl('#name-list button[data-id="dmm-3-23"]', 650, 0.35, 0.5);
    await at(8.72);
    mark("open");
    await click("ἀψίνθιον");
    await at(10.0);
    mark("passage");
    await focus(".passages .passage", "passage", 0, 12);
    const m0 = await box(".passages mark");
    await at(10.6);
    await moveTo(m0.x + 30, m0.y + 18, 800);
    await at(11.4);
    await moveTo(m0.x + m0.width * 0.85, m0.y + m0.height * 0.55, 2000);
    await at(17.2);
    mark("probs");
    const bar = await focus(".probs", "probabilities", 0, 18);
    await at(17.6);
    await moveTo(bar.x + bar.width * 0.5, bar.y + 34, 700);
    await at(21.3);
    await moveTo(bar.x + bar.width * 0.72, bar.y + 36, 600); // the 90% whisker
    await at(23.4);
    mark("unidentified");
    await moveTo(bar.x + bar.width * 0.28, bar.y + 92, 600);
    await at(26.4);
    mark("cands");
    const cTop = await docY(".cands");
    await scrollTo(cTop - 200, 1300);
    await focus(".cand", "candidate", 0, 10);
    await focus(".cand .contrib", "contrib", 0, 8);
    await at(30.3);
    await moveToEl(".cand .contrib span", 600, 0.5, 0.5, 0);
    await at(32.0);
    await moveToEl(".cand .contrib span", 600, 0.5, 0.5, 2);
    await at(33.9);
    mark("morph");
    await focus(".cand .morph", "description match", 0, 10);
    await moveToEl(".cand .morph span", 600, 0.5, 0.5, 0);
    await at(35.0);
    mark("eras");
    const eTop = await docY(".eras");
    await scrollTo(eTop - 110, 950);
    await focus(".eras", "eras-table", 0, 8);
    const skin = page.locator(".eras tbody tr", { hasText: "Skin & wounds" }).first();
    if (await skin.count()) { const sb = await skin.boundingBox(); focusBox(sb, "skin row", 8); await moveTo(sb.x + sb.width * 0.9, sb.y + sb.height / 2, 600); }
    await at(36.9);
    mark("galen");
    const gTop = await docY(".galen");
    await scrollTo(gTop - 150, 850);
    await focus(".galen", "galen", 0, 8);
    await moveTo(1060, 640, 600);
    await at(38.6);
    mark("modern");
    const mTop = await docY(".modern-list");
    await scrollTo(mTop - 560, 750);
    await focus(".modern-list", "villages", 0, 14);
    await moveToEl(".modern-list li", 600, 0.35, 0.5, 0);
    await at(41.2);
    mark("end");
    await stopClip();
  },

  // scene frames ~1212..1490 (s08_e: Dioscorides@1244, Galen@1280, John@1304, villages@1344)
  async time(page) {
    await open(page);
    const top = await topOf(page, "time");
    await jump(page, top + 40);
    await sleep(1800);
    await startClip("time", page, { x: 1150, y: 520 });
    mark("start");
    await scrollTo(top + 190, 800);
    await at(0.45);
    const chip = await box('#time .chip[data-ug="DE"]');
    await moveTo(chip.x + chip.width / 2, chip.y + chip.height / 2, 550);
    await at(1.1);
    await click("Skin & wounds");
    mark("skin");
    await focus(".alluvial-wrap", "alluvial", 0, 0);
    const col = async (txt) => { const l = page.locator("#alluvial text", { hasText: txt }).first(); return (await l.count()) ? l.boundingBox() : null; };
    const cols = { dio: await col("Dioscorides"), gal: await col("Galen"), john: await col("John"), mod: await col("Modern") };
    act("info", { columns: cols });
    if (cols.dio) await moveTo(cols.dio.x + cols.dio.width / 2, cols.dio.y + 60, 450);
    await at(2.0);
    if (cols.gal) await moveTo(cols.gal.x + cols.gal.width / 2, cols.gal.y + 60, 450);
    await at(2.8);
    if (cols.john) await moveTo(cols.john.x + cols.john.width / 2, cols.john.y + 60, 450);
    await at(4.1);
    if (cols.mod) await moveTo(cols.mod.x + cols.mod.width / 2, cols.mod.y + 60, 450);
    await at(5.3);
    const all = await box('#time .chip[data-ug="ALL"]');
    await moveTo(all.x + all.width / 2, all.y + all.height / 2, 500);
    await at(5.9);
    await click("All uses");
    mark("all");
    await at(6.6);
    mark("null");
    await focus(".null-card", "permutation", 0, 4);
    const nb = await box("#nullbars");
    act("focus", { x: Math.round(nb.x - 10), y: Math.round(nb.y - 10), w: Math.round(nb.width + 20), h: Math.round(nb.height / 3 + 10), label: "observed" });
    await moveTo(nb.x + nb.width * 0.55, nb.y + 24, 600);
    await at(9.6);
    mark("end");
    await stopClip();
  },

  // not in the VO edit; recorded for completeness (cutoff toggles change the verdict)
  async results(page) {
    await open(page);
    const top = await topOf(page, "results");
    await jump(page, top - 300);
    await sleep(1800);
    await startClip("results", page, { x: 1100, y: 640 });
    mark("start");
    await scrollTo(top + 300, 1500);
    let tt = 2.0;
    for (const y of ["2000", "2005", "2010", "2015"]) {
      await at(tt);
      await moveToEl(`#cutoffs .chip[data-cut="${y}"]`, 600);
      await click(y);
      mark(`cut${y}`);
      await focus("#fc-verdict", "verdict", 0, 6);
      tt += y === "2005" ? 3.4 : 2.6;
    }
    await at(tt);
    mark("end");
    await stopClip();
  },

  // scene frames 1490.. (s08_f@1490, g@1826, h@2174, i@2536)
  async leads(page) {
    const ctx = page.context();
    await open(page);
    const top = await topOf(page, "leads");
    await jump(page, top - 300);
    await sleep(1800);
    await allImages(page, "#lead-grid");
    await startClip("leads", page, { x: 1150, y: 640 });
    mark("start");
    await at(0.2);
    await scrollTo(top + 240, 1000);
    // certainty slider 0.20 -> 0.50   ("at least fifty percent sure" @1569-1598)
    await at(1.3);
    mark("slider");
    const s = await box("#pmin");
    await focus(".leads-tools", "tools", 0, 12);
    const vx = (v) => s.x + 8 + (s.width - 16) * (v / 0.9);
    const sy = s.y + s.height / 2;
    await moveTo(vx(0.2), sy, 600);
    await at(2.0);
    act("press", { x: Math.round(vx(0.2)), y: Math.round(sy), label: "drag" });
    await page.mouse.down();
    act("move", { x: Math.round(vx(0.5)), y: Math.round(sy), dur: 0.9 });
    for (let i = 1; i <= 36; i++) { await page.mouse.move(vx(0.2) + (vx(0.5) - vx(0.2)) * easeInOut(i / 36), sy); await wait(25); }
    await page.mouse.up();
    act("release", { x: Math.round(vx(0.5)), y: Math.round(sy) });
    rec.cursor = { x: vx(0.5), y: sy };
    let v = await page.$eval("#pmin", (e) => e.value);
    while (Number(v) < 0.5) { await page.keyboard.press("ArrowRight"); v = await page.$eval("#pmin", (e) => e.value); }
    while (Number(v) > 0.5) { await page.keyboard.press("ArrowLeft"); v = await page.$eval("#pmin", (e) => e.value); }
    act("info", { pmin: v });
    await focus(".range", "certainty", 0, 10);
    // hide toxic ("hides every plant with known toxicity" @1615-1655)
    // the warning a toxic lead carries (card row 2: scroll it up into view), then hide them all
    await at(3.1);
    mark("toxtag");
    const tox = page.locator("#lead-grid .tag.tox").first();
    if (await tox.count()) {
      await scrollTo(top + 240 + 330, 450);
      const xb = await tox.boundingBox();
      focusBox(xb, "tox tag", 10);
      focusBox(await page.locator("#lead-grid .lead:has(.tag.tox)").first().boundingBox(), "tox card", 8);
      act("info", { toxicLead: await page.locator("#lead-grid .lead:has(.tag.tox)").first().getAttribute("aria-label") });
      await moveTo(xb.x + xb.width * 0.5, xb.y + xb.height * 0.6, 400);
      await at(4.15);
      await scrollTo(top + 240, 450);
    }
    await at(4.62);
    mark("hide");
    await focus(".toggle", "toxicity toggle", 0, 10);
    await moveToEl("#hide-tox", 450);
    await at(5.2);
    await click("Hide plants with known toxicity");
    await page.locator("#hide-tox").check();
    // condition ("picks a condition" @1688-1710)
    await at(5.8);
    mark("cond");
    await moveToEl("#lead-cond", 550, 0.4, 0.5);
    await at(6.5);
    await click("condition");
    await at(6.7);
    await page.selectOption("#lead-cond", "Eye Diseases");
    act("select", { label: "Eye Diseases", x: Math.round(rec.cursor.x), y: Math.round(rec.cursor.y) });
    mark("cards");
    await at(7.6);
    // rank 4 (Artemisia absinthium · Eye Diseases: the same lead the "Under the hood" scene traces), else the
    // best-ranked card with a compound -> target path
    let idx = await page.$$eval("#lead-grid .lead", (ls) => ls.findIndex((l) => l.dataset.rank === "4" && l.textContent.includes("Compound → target path")));
    if (idx < 0) idx = await page.$$eval("#lead-grid .lead", (ls) => ls.findIndex((l) => l.textContent.includes("Compound → target path")));
    const cardL = page.locator("#lead-grid .lead").nth(idx);
    act("info", { lead: await cardL.getAttribute("aria-label"), cardIndex: idx });
    focusBox(await cardL.boundingBox(), "card", 8);
    focusBox(await page.locator("#lead-grid").boundingBox(), "grid", 0);
    await moveTo(1250, 700, 900);
    // "how sure we are of the plant" @1854-1881  (t = (f-1490)/30)
    await at(11.9);
    mark("meters");
    const meters = cardL.locator(".meters");
    const mb = await meters.boundingBox();
    focusBox(mb, "meters", 10);
    await moveTo(mb.x + mb.width * 0.55, mb.y + mb.height * 0.25, 600);
    // "whether a full chain exists" @1905
    await at(13.6);
    mark("pathtag");
    const tag = cardL.locator(".tag", { hasText: "Compound → target path" });
    const tb = await tag.boundingBox();
    focusBox(tb, "path tag", 10);
    await moveTo(tb.x + tb.width * 0.5, tb.y + tb.height * 0.6, 600);
    // "She opens one" @2181
    await at(22.2);
    mark("open");
    const cb = await cardL.boundingBox();
    await moveTo(cb.x + cb.width * 0.5, cb.y + cb.height * 0.32, 600);
    await at(23.0);
    await click("open lead");
    await at(23.7);
    mark("dialog");
    await focus("dialog.paths", "dialog", 0, 0);
    await focus("dialog.paths > p", "no paper", 0, 10);
    await moveTo(1000, 640, 700);
    // "the exact search" @2292
    await at(25.9);
    mark("query");
    await focus("dialog.paths code", "query", 0, 10);
    await moveToEl("dialog.paths code", 500, 0.35, 0.5);
    await at(26.8);
    const link = page.locator("dialog.paths a", { hasText: "Run this query on PubMed" });
    await link.scrollIntoViewIfNeeded();
    const lb = await link.boundingBox();
    act("info", { pubmedLink: lb });
    await moveTo(lb.x + lb.width * 0.5, lb.y + lb.height * 0.5, 500);
    await at(27.4);
    mark("pubmed_click");
    let [pop] = await Promise.all([ctx.waitForEvent("page", { timeout: 6000 }).catch(() => null), click("Run this query on PubMed")]);
    if (!pop) {
      // the site's .cta-row::before glow (inset -40px) sits over this link and swallows pointer clicks
      console.log("  SITE BUG: pointer click on the PubMed link is intercepted by .cta-row::before; activating the link directly");
      act("info", { siteBug: ".cta-row::before (inset:-40px) intercepts clicks on 'Run this query on PubMed'; link activated via element.click()" });
      [pop] = await Promise.all([ctx.waitForEvent("page", { timeout: 20000 }), link.evaluate((a) => a.click())]);
    }
    act("info", { pubmed_url: await link.getAttribute("href") });
    mark("away");
    // ---- PubMed, real result page in the new tab: its own clip (starts once loaded: no dead time)
    await pop.waitForLoadState("load");
    // PubMed first serves a "Checking your browser" interstitial that redirects itself; record only the real page
    await pop.waitForFunction(() => document.body && !/Checking your browser/i.test(document.body.innerText) && /results|No results were found/i.test(document.body.innerText), null, { timeout: 90000 }).catch(() => console.log("  PubMed still on the interstitial"));
    await pop.waitForLoadState("networkidle", { timeout: 25000 }).catch(() => {});
    await sleep(1200);
    const main = rec; rec = null;
    await startClip("pubmed", pop, { x: 1100, y: 600 });
    mark("start");
    const result = await pop.evaluate(() => {
      const t = document.body.innerText;
      const amt = document.querySelector(".results-amount");
      return { no_results: /No results were found/i.test(t), results_amount: amt ? amt.innerText.trim() : null, query_box: document.querySelector("#id_term")?.value ?? null, excerpt: t.slice(0, 500) };
    });
    act("info", { pubmed: result });
    console.log("PubMed:", JSON.stringify(result).slice(0, 300));
    const msg = pop.locator("text=/No results were found/i").first();
    if (await msg.count()) {
      const mbx = await msg.boundingBox();
      focusBox(mbx, "no results", 18);
      await moveTo(mbx.x + mbx.width * 0.5, mbx.y + mbx.height + 26, 900);
    } else {
      await moveTo(900, 420, 900);
    }
    await at(4.0);
    mark("end");
    await stopClip();
    await pop.close();
    rec = main;
    // ---- back on the site ("the chemistry already points at a target" @2370-2412)
    await page.bringToFront();
    const b0 = Math.ceil(ct() + 0.3);
    await at(b0);
    mark("back");
    await focus("dialog.paths .path-row", "path", 0, 8);
    await moveToEl("dialog.paths .path-row", 600, 0.5, 0.5, 0);
    await at(b0 + 3.4);
    mark("close");
    await moveToEl("dialog.paths .close", 600);
    await at(b0 + 4.1);
    await click("Close");
    await page.evaluate(() => document.querySelector("dialog.paths").close());
    // "She downloads the shortlist" @2542
    await at(b0 + 4.8);
    mark("csv");
    await moveToEl("#csv", 800);
    await at(b0 + 5.8);
    const [dl] = await Promise.all([page.waitForEvent("download"), click("Download CSV")]);
    await focus("#csv", "csv", 0, 10);
    await dl.saveAs(path.join(__dirname, "pharmakon_leads.csv"));
    act("info", { download: dl.suggestedFilename() });
    await at(b0 + 7.8);
    mark("end");
    await stopClip();
  },

  async use(page) {
    await open(page);
    const top = await topOf(page, "use");
    await jump(page, top + 20);
    await sleep(1800);
    await startClip("use", page, { x: 1150, y: 700 });
    mark("start");
    await scrollTo(top + 160, 900);
    await focus(".use-card pre", "mcp command", 0, 10);
    await at(0.6);
    await moveToEl(".use-card pre", 700, 0.3, 0.45, 0);
    await at(1.8);
    await moveToEl(".use-card pre", 700, 0.75, 0.6, 0);
    await at(3.6);
    mark("end");
    await stopClip();
  },

  async github(page) {
    await page.goto("https://github.com/LSUDOKO/Pharmakon", { waitUntil: "load" });
    await page.waitForLoadState("networkidle", { timeout: 20000 }).catch(() => {});
    for (let y = 0; y < 9000; y += 600) { await jump(page, y); await sleep(200); }
    await allImages(page, "article.markdown-body");
    const readmeTop = await page.evaluate(() => { const a = document.querySelector("article.markdown-body"); return a ? a.getBoundingClientRect().top + scrollY : 900; });
    await jump(page, readmeTop - 90);
    await sleep(2000);
    await startClip("github", page, { x: 1250, y: 700 });
    mark("start");
    await focus("article.markdown-body", "readme", 0, 0);
    const resY = await page.evaluate(() => {
      const hs = [...document.querySelectorAll("article.markdown-body h2, article.markdown-body h3")];
      const h = hs.find((e) => /result/i.test(e.textContent)) || document.querySelector("article.markdown-body table");
      return h ? h.getBoundingClientRect().top + scrollY : 3000;
    });
    act("info", { readmeTop, resultsY: resY });
    await at(2.4);
    mark("scroll");
    await scrollTo(resY - 110, 4000);
    mark("tables");
    await focus("article.markdown-body table", "results table", 0, 8).catch(() => {});
    await moveTo(900, 520, 900);
    await at(9.5);
    mark("end");
    await stopClip();
  },
};

(async () => {
  const want = process.argv.slice(2);
  const order = want.length ? want : ["explorer", "time", "leads", "use", "github", "results"];
  const browser = await chromium.launch({
    channel: "chrome", headless: true,
    args: ["--hide-scrollbars", "--force-color-profile=srgb", "--use-gl=angle", "--use-angle=gl-egl", "--enable-gpu", "--ignore-gpu-blocklist"],
  });
  const ctx = await newContext(browser);
  const page = await ctx.newPage();
  await warm(page);
  for (const name of order) {
    await CLIPS[name](page);
  }
  await browser.close();
  for (const enc of PENDING) enc();
  console.log("encoded", PENDING.length, "clips");
})().catch((e) => { console.error(e); process.exit(1); });
