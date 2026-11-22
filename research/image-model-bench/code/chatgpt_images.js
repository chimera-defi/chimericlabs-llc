// Drive ChatGPT image generation through a Chrome you already signed in to. Selectors checked against live chatgpt.com 2026-11-22 (composer, send, image, blob fetch); full Playwright run not possible from the extension.
// Sign-in stays manual: start Chrome with --remote-debugging-port=9222, log in yourself, then:
//   node chatgpt_images.js prompts.txt out_dir      (one prompt per line; ~70 s per image)
// Needs: npm i playwright. Selectors are the likeliest to break; they live in SEL below.
const { chromium } = require('playwright');
const fs = require('fs');
const SEL = {
  box: 'div.ProseMirror[contenteditable="true"]',  // #prompt-textarea no longer exists
  send: 'form button[aria-label="Send"]',  // no data-testid now
  image: 'img[alt^="Generated image"]',  // src is a blob: URL
  stop: 'form button[aria-label="Stop"]',  // stays up >70 s after the image is complete
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
    await page.click(SEL.box);
    await page.keyboard.insertText(p);  // fill() is unreliable on ProseMirror
    await page.click(SEL.send);
    await page.waitForFunction(([s, n]) => document.querySelectorAll(s).length > n, [SEL.image, seen], { timeout: 240000 });
    await page.waitForTimeout(3000);  // do not wait for Stop: it lingers; blob is complete once the img appears
    // src is blob:, so fetch inside the page (page.request cannot read blob URLs)
    const b64 = await page.locator(SEL.image).last().evaluate(async el => {
      const u = new Uint8Array(await (await (await fetch(el.src)).blob()).arrayBuffer());
      let s = ''; for (let k = 0; k < u.length; k += 32768) s += String.fromCharCode(...u.subarray(k, k + 32768));
      return btoa(s);
    });
    const buf = Buffer.from(b64, 'base64');
    fs.writeFileSync(`${outDir}/${String(i + 1).padStart(2, '0')}.png`, buf);
    console.log(`${i + 1}/${prompts.length} ${((Date.now() - t0) / 1000).toFixed(0)} s ${buf.length} bytes`);
  }
  await browser.close();
})();
