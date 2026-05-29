/**
 * Lighthouse User Flow Templates
 *
 * Three ready-to-use templates demonstrating the startFlow API modes
 * documented at https://web.dev/articles/lighthouse-user-flows.
 *
 * Dependencies:
 *   npm install puppeteer lighthouse
 *
 * Usage:
 *   Copy the template you need, adjust URLs/selectors, and run with Node:
 *   node user-flow-templates.js
 */

const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

// ──────────────────────────────────────────────────────────────────────
// Template A: Cold + Warm Navigation Flow
//
// Runs TWO navigations to the same URL:
//   1. Cold load — cache cleared, fresh connection (default behaviour)
//   2. Warm load — cache and connections preserved via disableStorageReset
//
// The unified report shows both steps side-by-side so you can compare
// first-visit vs. repeat-visit performance (LCP, FCP, Speed Index).
// ──────────────────────────────────────────────────────────────────────
async function coldWarmNavigationFlow() {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-gpu'],
  });

  try {
    const page = await browser.newPage();
    const { startFlow } = require('lighthouse');

    const flow = await startFlow(page, {
      name: 'Cold vs Warm Navigation',
      configContext: {
        settings: { preset: 'desktop' },
      },
    });

    // Step 1: Cold navigation (default — clears cache, storage, connections)
    console.log('[Cold+Warm] Step 1: Cold navigation...');
    await flow.navigate('https://example.com', {
      stepName: 'Cold Load (cache cleared)',
    });

    // Step 2: Warm navigation — keeps cache and service workers intact
    console.log('[Cold+Warm] Step 2: Warm navigation (disableStorageReset)...');
    await flow.navigate('https://example.com', {
      stepName: 'Warm Load (cached)',
      configContext: {
        settings: {
          disableStorageReset: true,
        },
      },
    });

    // Save reports
    const reportsDir = path.join(__dirname, '..', 'reports');
    fs.mkdirSync(reportsDir, { recursive: true });

    const flowResult = await flow.createFlowResult();
    fs.writeFileSync(
      path.join(reportsDir, 'cold_warm_flow.json'),
      JSON.stringify(flowResult, null, 2)
    );

    const html = await flow.generateReport();
    fs.writeFileSync(path.join(reportsDir, 'cold_warm_flow.html'), html);

    console.log('[Cold+Warm] Reports saved to reports/cold_warm_flow.*');
    return flowResult;
  } finally {
    await browser.close();
  }
}

// ──────────────────────────────────────────────────────────────────────
// Template B: Snapshot Flow
//
// Navigates to a page, performs interactions to reach a specific UI
// state (e.g. open a modal, fill a form, expand a panel), then takes
// a Lighthouse snapshot.
//
// Snapshots DO NOT trigger a page load — they audit the current DOM
// in place. This is ideal for:
//   - Accessibility audits on a modal dialog
//   - Best-practices checks on a half-completed checkout form
//   - SEO audits after client-side rendering completes
//
// Available categories in snapshot mode:
//   accessibility, best-practices, seo
// Performance scores are NOT available (no navigation occurs).
// ──────────────────────────────────────────────────────────────────────
async function snapshotFlow() {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-gpu'],
  });

  try {
    const page = await browser.newPage();
    const { startFlow } = require('lighthouse');

    const flow = await startFlow(page, {
      name: 'Snapshot — Checkout Form Mid-Completion',
      configContext: {
        settings: { preset: 'desktop' },
      },
    });

    // Step 1: Navigate to the checkout page (standard navigation audit)
    console.log('[Snapshot] Step 1: Navigate to checkout page...');
    await flow.navigate('https://example.com/checkout', {
      stepName: 'Checkout Page Load',
    });

    // Step 2: Interact with the page to reach the desired state
    console.log('[Snapshot] Step 2: Filling checkout form...');
    await page.type('#first-name', 'Jane');
    await page.type('#last-name', 'Doe');
    await page.type('#email', 'jane.doe@example.com');
    await page.select('#country', 'US');

    // Open a dropdown or expand a section
    const shippingToggle = await page.$('#shipping-options-toggle');
    if (shippingToggle) {
      await shippingToggle.click();
      await page.waitForSelector('#shipping-options-panel', { visible: true });
    }

    // Step 3: Take a snapshot of the current page state
    console.log('[Snapshot] Step 3: Capturing snapshot...');
    await flow.snapshot({
      stepName: 'Checkout Form — Mid-Completion State',
    });

    // Save reports
    const reportsDir = path.join(__dirname, '..', 'reports');
    fs.mkdirSync(reportsDir, { recursive: true });

    const flowResult = await flow.createFlowResult();
    fs.writeFileSync(
      path.join(reportsDir, 'snapshot_flow.json'),
      JSON.stringify(flowResult, null, 2)
    );

    const html = await flow.generateReport();
    fs.writeFileSync(path.join(reportsDir, 'snapshot_flow.html'), html);

    console.log('[Snapshot] Reports saved to reports/snapshot_flow.*');
    return flowResult;
  } finally {
    await browser.close();
  }
}

// ──────────────────────────────────────────────────────────────────────
// Template C: Timespan Flow
//
// Starts a measurement window, performs user interactions, then ends
// the window. Lighthouse records metrics DURING the interaction
// period rather than during a page load.
//
// Timespan captures:
//   - CLS (Cumulative Layout Shift) caused by interactions
//   - TBT (Total Blocking Time) during the period
//   - INP (Interaction to Next Paint)
//   - Long tasks and layout shifts triggered by scrolling, clicking,
//     typing, or lazy-loading content
//
// Use cases:
//   - Measuring layout shift during infinite scroll
//   - Checking blocking time when expanding an accordion
//   - Auditing responsiveness of a search-as-you-type feature
// ──────────────────────────────────────────────────────────────────────
async function timespanFlow() {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-gpu'],
  });

  try {
    const page = await browser.newPage();
    const { startFlow } = require('lighthouse');

    const flow = await startFlow(page, {
      name: 'Timespan — Product Scroll Interaction',
      configContext: {
        settings: { preset: 'desktop' },
      },
    });

    // Navigate to the page first (outside the timespan so navigation
    // metrics don't pollute the interaction measurement)
    console.log('[Timespan] Navigating to products page...');
    await page.goto('https://example.com/products', {
      waitUntil: 'networkidle0',
    });

    // Step 1: Start the timespan measurement
    console.log('[Timespan] Step 1: Starting timespan...');
    await flow.startTimespan({
      stepName: 'Product Scroll & Filter Interactions',
    });

    // Step 2: Perform interactions while Lighthouse records metrics
    console.log('[Timespan] Step 2: Scrolling and interacting...');

    // Scroll down to trigger lazy-loaded content
    for (let i = 0; i < 5; i++) {
      await page.evaluate(() => window.scrollBy(0, 800));
      // Small pause to allow content to load and layout shifts to occur
      await new Promise((r) => setTimeout(r, 500));
    }

    // Click a filter button
    const filterBtn = await page.$('[data-filter="electronics"]');
    if (filterBtn) {
      await filterBtn.click();
      await new Promise((r) => setTimeout(r, 1000));
    }

    // Scroll back to top
    await page.evaluate(() => window.scrollTo(0, 0));
    await new Promise((r) => setTimeout(r, 500));

    // Step 3: End the timespan measurement
    console.log('[Timespan] Step 3: Ending timespan...');
    await flow.endTimespan();

    // Save reports
    const reportsDir = path.join(__dirname, '..', 'reports');
    fs.mkdirSync(reportsDir, { recursive: true });

    const flowResult = await flow.createFlowResult();
    fs.writeFileSync(
      path.join(reportsDir, 'timespan_flow.json'),
      JSON.stringify(flowResult, null, 2)
    );

    const html = await flow.generateReport();
    fs.writeFileSync(path.join(reportsDir, 'timespan_flow.html'), html);

    console.log('[Timespan] Reports saved to reports/timespan_flow.*');
    return flowResult;
  } finally {
    await browser.close();
  }
}

// ──────────────────────────────────────────────────────────────────────
// Main — run all three templates or pick one via CLI argument
// Usage:
//   node user-flow-templates.js              (runs all three)
//   node user-flow-templates.js cold-warm
//   node user-flow-templates.js snapshot
//   node user-flow-templates.js timespan
// ──────────────────────────────────────────────────────────────────────
(async () => {
  const arg = process.argv[2];

  try {
    if (!arg || arg === 'cold-warm') {
      await coldWarmNavigationFlow();
    }
    if (!arg || arg === 'snapshot') {
      await snapshotFlow();
    }
    if (!arg || arg === 'timespan') {
      await timespanFlow();
    }
    console.log('\nAll requested flows completed successfully.');
  } catch (err) {
    console.error('Flow execution failed:', err);
    process.exit(1);
  }
})();
