// Chơi trọn 1 Ngày trên chonoi.live (--mode day --days 1) và chụp màn hình các màn phủ bằng Edge headless + DevTools.
// Phím thật (Enter, H, 1) đi qua Input.dispatchKeyEvent; di chuyển nhân vật qua POST /input (cùng API trình duyệt dùng).
// node playday.mjs <port game> <thư mục ảnh> <edge.exe> <profile dir>
import { spawn } from "node:child_process";
import { writeFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const [, , PORT, OUT, EDGE, PROFILE] = process.argv;
const GAME = `http://127.0.0.1:${PORT}`;
const DBG = 9333;
mkdirSync(OUT, { recursive: true });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const log = (...a) => console.log(new Date().toISOString().slice(11, 19), ...a);

const edge = spawn(EDGE, ["--headless=new", "--disable-gpu", "--hide-scrollbars", `--remote-debugging-port=${DBG}`,
  `--user-data-dir=${PROFILE}`, "--window-size=1400,800", "about:blank"], { stdio: "ignore" });
let ws, seq = 0; const waiting = new Map();
async function connect() {
  for (let i = 0; i < 50; i++) {
    try {
      const list = await (await fetch(`http://127.0.0.1:${DBG}/json/list`)).json();
      const page = list.find((t) => t.type === "page");
      if (page) { ws = new WebSocket(page.webSocketDebuggerUrl); break; }
    } catch { /* Edge chưa lên */ }
    await sleep(200);
  }
  await new Promise((r) => ws.addEventListener("open", r, { once: true }));
  ws.addEventListener("message", (m) => { const d = JSON.parse(m.data); if (d.id && waiting.has(d.id)) { waiting.get(d.id)(d); waiting.delete(d.id); } });
}
const cdp = (method, params = {}) => new Promise((r) => { const id = ++seq; waiting.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const KEYS = { Enter: ["Enter", "Enter", 13, "\r"], h: ["h", "KeyH", 72, "h"], 1: ["1", "Digit1", 49, "1"] };
async function key(k) {
  const [key, code, vk, text] = KEYS[k];
  await cdp("Input.dispatchKeyEvent", { type: "keyDown", key, code, windowsVirtualKeyCode: vk, text });
  await sleep(60);
  await cdp("Input.dispatchKeyEvent", { type: "keyUp", key, code, windowsVirtualKeyCode: vk });
  await sleep(250);
}
async function shot(name) {
  await sleep(400);
  const r = await cdp("Page.captureScreenshot", { format: "png" });
  writeFileSync(join(OUT, name), Buffer.from(r.result.data, "base64"));
  log("ảnh", name);
}
const state = async () => (await fetch(GAME + "/state")).json();
const input = (o) => fetch(GAME + "/input", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ interact: false, catch: false, ...o }) });
async function press() { await input({ move: [0, 0], interact: true }); await sleep(90); await input({ move: [0, 0] }); await sleep(90); }
async function walk(tx, ty, axis) {  // gather: [x, d] ; quan: [x, z]
  for (let i = 0; i < 400; i++) {
    const s = await state(); const p = s.player.pos;
    if (s.phase !== axis) return false;
    const dx = tx - p[0], dy = ty - p[1];
    if (Math.abs(dx) < 0.4 && Math.abs(dy) < 0.4) break;
    await input({ move: [Math.sign(Math.abs(dx) > 0.3 ? dx : 0), Math.sign(Math.abs(dy) > 0.3 ? dy : 0)] });
    await sleep(40);
  }
  await input({ move: [0, 0] }); return true;
}
const waitFor = async (pred, ms = 400000) => { const t0 = Date.now(); while (Date.now() - t0 < ms) { const s = await state(); if (pred(s)) return s; await sleep(150); } throw new Error("hết giờ chờ"); };

await connect();
await cdp("Page.enable");
await cdp("Page.navigate", { url: GAME + "/" });
await sleep(1500);
await shot("01-menu.png");
await key("Enter"); await shot("02-dayintro.png");
await key("Enter"); await sleep(300);
log("state sau Enter:", (await state()).state);

// --- buổi sáng: hái bông súng N3 (44) / N4 (60) ở mặt nước, gần hết giờ về bến cất đồ ---
let hcDone = false;
while (true) {
  const s = await state();
  if (s.phase !== "gather") break;
  if (s.time_left_ticks < 60 * 22) {
    await walk(2, 0, "gather"); await press(); log("cập bến → pha", (await state()).phase);
    await waitFor((x) => x.phase !== "gather"); break;
  }
  for (const n of (s.nodes || []).filter((n) => n.kind === "bong_sung")) {
    if (n.ready === false) continue;
    if (!(await walk(n.pos[0], 0, "gather"))) break;
    await press();
  }
  if (!hcDone && (s.hold || []).length >= 2) {  // chế độ tương phản cao bằng phím H thật
    await key("h"); await shot("07-high-contrast.png"); await key("h"); hcDone = true;
  }
  await sleep(300);
}
await waitFor((x) => x.phase === "quan");
await shot("03-evening.png");
await key("Enter");

// --- buổi tối: nấu → bưng → phục vụ ---
const tablePos = {};
while (true) {
  const s = await state();
  if (s.phase !== "quan") break;
  (s.tables || []).forEach((t) => (tablePos[t.id] = t.pos));
  const cust = s.customers || [];
  if (s.hand) {
    const c = cust.find((c) => c.id === s.hand.order_id);
    if (c) { const t = tablePos[c.table_id]; await walk(t[0], t[1] + 1.2, "quan"); await press(); log("phục vụ", c.table_id); }
    continue;
  }
  const ready = (s.stoves || []).find((st) => st.state === "ready");
  if (ready) { await walk(ready.pos[0], ready.pos[1] - 1, "quan"); await press(); continue; }
  const idle = (s.stoves || []).find((st) => st.state === "idle");
  if (idle && cust.some((c) => c.order_status === "reserved")) { await walk(idle.pos[0], idle.pos[1] - 1, "quan"); await press(); continue; }
  await sleep(300);
}
await waitFor((x) => x.phase === "shop" || x.finished);
await shot("04-day-result.png");
await key("Enter"); await sleep(300);
await key("1"); await shot("05-shop.png");
await key("Enter");
await waitFor((x) => x.finished, 30000);
await shot("06-summary.png");
const end = await state();
log("kết thúc:", JSON.stringify({ reason: end.reason, score: end.score, earned: end.earned, reputation: end.reputation, history: end.history }));
ws.close(); edge.kill();
process.exit(0);
