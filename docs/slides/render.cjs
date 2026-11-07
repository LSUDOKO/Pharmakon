// Render docs/slides/deck.html to a PDF and per-slide PNG previews.
// Usage: node docs/slides/render.cjs [path-to-playwright]
const path = require("path");
const pw = process.argv[2] || "playwright";
const { chromium } = require(pw);
(async () => {
  const dir = __dirname;
  const browser = await chromium.launch({ channel: "chrome", headless: true });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto("file://" + path.join(dir, "deck.html"), { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(1500);
  await page.pdf({ path: path.join(dir, "Pharmakon_EthnoHack2026_slides.pdf"), width: "1920px", height: "1080px", printBackground: true, preferCSSPageSize: true });
  const n = await page.locator("section.slide").count();
  for (let i = 0; i < n; i++) await page.locator("section.slide").nth(i).screenshot({ path: path.join(dir, "preview", `slide-${String(i + 1).padStart(2, "0")}.png`) });
  await browser.close();
  console.log("pages:", n);
})();
