// Drive ChatGPT image generation through a Chrome you already signed in to. UNTESTED against the live site.
// Sign-in stays manual: start Chrome with --remote-debugging-port=9222, log in yourself, then:
//   node chatgpt_images.js prompts.txt out_dir      (one prompt per line; ~70 s per image)
// Needs: npm i playwright. Selectors are the likeliest to break; they live in SEL below.
const { chromium } = require('playwright');
const fs = require('fs');
const SEL = {
  box: '#prompt-textarea',
  send: 'button[data-testid="send-button"]',
  image: 'img[alt*="Generated image" i], img[alt*="image" i][src*="oaiusercontent"], img[src*="files.oaiusercontent"]',
  stop: 'button[data-testid="stop-button"]',
};
(async () => {
  const [promptFile, outDir] = process.argv.slice(2);
  fs.mkdirSync(outDir, { recursive: true });
  const prompts = fs.readFileSync(promptFile, 'utf8').split('\n').filter(Boolean);
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const page = browser.contexts()[0].pages().find(p => p.url().includes('chatgpt.com')) || await browser.contexts()[0].newPage();
  if (!page.url().includes('chatgpt.com')) await page.goto('https://chatgpt.com/');
  for (const [i, p] of prompts.entries()) {
    const seen = await page.locator(SEL.image).count();
    const t0 = Date.now();
    await page.fill(SEL.box, p);
    await page.click(SEL.send);
    await page.waitForFunction(([s, n]) => document.querySelectorAll(s).length > n, [SEL.image, seen], { timeout: 240000 });
    await page.waitForSelector(SEL.stop, { state: 'detached', timeout: 240000 }).catch(() => {});
    const src = await page.locator(SEL.image).last().getAttribute('src');
    const buf = Buffer.from(await (await page.request.get(src)).body());
    fs.writeFileSync(`${outDir}/${String(i + 1).padStart(2, '0')}.png`, buf);
    console.log(`${i + 1}/${prompts.length} ${((Date.now() - t0) / 1000).toFixed(0)} s ${buf.length} bytes`);
  }
  await browser.close();
})();
