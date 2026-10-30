let chromium;
try {
  ({ chromium } = await import("playwright"));
} catch {
  ({ chromium } = await import("file:///C:/Users/Hrushikesh Mirji/AppData/Local/npm-cache/_npx/9833c18b2d85bc59/node_modules/playwright/index.mjs"));
}

async function run() {
  console.log("=== PLAYWRIGHT SMOKE TEST (PORT 5174) ===");
  const browser = await chromium.launch({ channel: "msedge", headless: true });
  
  const viewports = [
    { name: "Desktop", width: 1280, height: 800 },
    { name: "Mobile (iPhone 12/13/14)", width: 390, height: 844 }
  ];

  const routes = [
    "/",
    "/detection",
    "/dashboard",
    "/diseases",
    "/research",
    "/admin"
  ];

  let totalErrors = 0;

  for (const vp of viewports) {
    console.log(`\nTesting Viewport: ${vp.name} (${vp.width}x${vp.height})`);
    const context = await browser.newContext({
      viewport: { width: vp.width, height: vp.height },
      userAgent: vp.name.includes("Mobile")
        ? "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
        : undefined
    });

    const page = await context.newPage();
    const consoleMessages = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        consoleMessages.push(msg.text());
      }
    });

    for (const route of routes) {
      consoleMessages.length = 0;
      const url = `http://localhost:5174${route}`;
      try {
        const resp = await page.goto(url, { waitUntil: "networkidle", timeout: 10000 });
        const currentUrl = page.url();
        const title = await page.title();
        console.log(`  Route: ${route}`);
        console.log(`    Status: ${resp ? resp.status() : "N/A"}`);
        console.log(`    Resolved URL: ${currentUrl}`);
        console.log(`    Title: "${title}"`);
        console.log(`    Console Errors: ${consoleMessages.length}`);
        if (consoleMessages.length > 0) {
          totalErrors += consoleMessages.length;
          consoleMessages.forEach(e => console.log(`      ERROR: ${e}`));
        }
      } catch (err) {
        console.log(`    FAILED: ${err.message}`);
        totalErrors++;
      }
    }
    await context.close();
  }

  await browser.close();
  console.log(`\nPlaywright run complete. Total uncaught console errors: ${totalErrors}`);
}

run().catch((err) => {
  console.error("Playwright error:", err);
  process.exit(1);
});
