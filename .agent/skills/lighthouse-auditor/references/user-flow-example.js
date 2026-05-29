const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

(async () => {
  console.log('Launching browser...');
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-gpu']
  });
  
  try {
    const page = await browser.newPage();

    // Dynamically load startFlow from Lighthouse
    const { startFlow } = require('lighthouse');

    console.log('Initializing user flow...');
    const flow = await startFlow(page, {
      name: 'Authenticated Dashboard Flow',
      configContext: {
        settings: {
          preset: 'desktop',
        },
      },
    });

    // 1. Initial login page navigation (Standard Puppeteer without Lighthouse tracking)
    console.log('Navigating to login page...');
    await page.goto('https://example.com/login', { waitUntil: 'networkidle0' });

    // 2. Perform Login actions using Puppeteer
    console.log('Submitting credentials...');
    await page.type('#username', 'testuser');
    await page.type('#password', 'password123');
    
    await Promise.all([
      page.click('#submit-btn'),
      page.waitForNavigation({ waitUntil: 'networkidle0' })
    ]);

    // 3. Run Navigation-mode audit on the dashboard now that we are authenticated
    console.log('Auditing authenticated Dashboard page...');
    await flow.navigate('https://example.com/dashboard', {
      stepName: 'Dashboard Page Load'
    });

    // Create reports directory if it doesn't exist
    const reportsDir = path.join(__dirname, '..', 'reports');
    if (!fs.existsSync(reportsDir)) {
      fs.mkdirSync(reportsDir, { recursive: true });
    }

    // 4. Save JSON flow results
    console.log('Generating JSON report...');
    const flowResult = await flow.createFlowResult();
    const jsonPath = path.join(reportsDir, 'user_flow_report.json');
    fs.writeFileSync(jsonPath, JSON.stringify(flowResult, null, 2));
    console.log(`Saved JSON report to ${jsonPath}`);

    // 5. Generate and save HTML flow report
    console.log('Generating HTML report...');
    const htmlReport = await flow.generateReport();
    const htmlPath = path.join(reportsDir, 'user_flow_report.html');
    fs.writeFileSync(htmlPath, htmlReport);
    console.log(`Saved HTML report to ${htmlPath}`);

  } catch (error) {
    console.error('Error executing user flow:', error);
    process.exit(1)
  } finally {
    await browser.close();
    console.log('Browser closed.');
  }
})();
