import os
import sys
import json
import subprocess
import urllib.parse
from datetime import datetime
from robot.api.deco import keyword

class lighthouse_keywords:
    ROBOT_LIBRARY_SCOPE = 'SUITE'

    @keyword("Run Lighthouse Audit")
    def run_lighthouse_audit(self, url, preset="mobile"):
        """
        Runs npx lighthouse via subprocess and returns the parsed JSON report.
        """
        parsed_url = urllib.parse.urlparse(url)
        safe_host = parsed_url.netloc.replace(":", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        report_dir = "reports"
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, f"lh_{safe_host}_{timestamp}")
        
        cmd = [
            "npx", "lighthouse", url,
            "--output=json",
            f"--output-path={report_path}",
            "--chrome-flags=--headless --no-sandbox --disable-gpu"
        ]
        
        if preset == "desktop":
            cmd.append("--preset=desktop")
            
        is_windows = (sys.platform == "win32" or os.name == "nt")
        try:
            subprocess.run(cmd, shell=is_windows, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Lighthouse execution failed: {e.stderr.decode('utf-8', errors='ignore')}")

        actual_json_path = f"{report_path}.report.json"
        if not os.path.exists(actual_json_path):
            actual_json_path = f"{report_path}.json"
            
        if not os.path.exists(actual_json_path):
            raise FileNotFoundError(f"Lighthouse report not found at expected path: {actual_json_path}")
            
        with open(actual_json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @keyword("Run Authenticated Lighthouse Audit")
    def run_authenticated_lighthouse_audit(self, url, login_url, username, password,
                                           username_selector, password_selector, submit_selector,
                                           preset="mobile"):
        """
        Authenticates via Playwright, extracts session cookies, injects them into Lighthouse
        extra headers, and runs the audit.
        """
        from playwright.sync_api import sync_playwright

        cookies = []
        with sync_playwright() as p:
            # Launch headless browser
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            
            # Navigate to login page
            page.goto(login_url)
            
            # Fill credentials
            page.fill(username_selector, username)
            page.fill(password_selector, password)
            
            # Submit login form
            page.click(submit_selector)
            
            # Wait for redirect/navigation (or stable network)
            page.wait_for_load_state("networkidle")
            
            # Extract cookies
            cookies = context.cookies()
            browser.close()
            
        if not cookies:
            raise RuntimeError("Failed to retrieve cookies after authentication")
            
        # Format cookies for Lighthouse --extra-headers
        cookie_string = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
        headers = json.dumps({"Cookie": cookie_string})
        
        # Run Lighthouse with the headers
        parsed_url = urllib.parse.urlparse(url)
        safe_host = parsed_url.netloc.replace(":", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        report_dir = "reports"
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, f"lh_auth_{safe_host}_{timestamp}")
        
        cmd = [
            "npx", "lighthouse", url,
            "--output=json",
            f"--output-path={report_path}",
            f"--extra-headers={headers}",
            "--chrome-flags=--headless --no-sandbox --disable-gpu"
        ]
        
        if preset == "desktop":
            cmd.append("--preset=desktop")
            
        is_windows = (sys.platform == "win32" or os.name == "nt")
        try:
            subprocess.run(cmd, shell=is_windows, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Lighthouse authenticated audit failed: {e.stderr.decode('utf-8', errors='ignore')}")

        actual_json_path = f"{report_path}.report.json"
        if not os.path.exists(actual_json_path):
            actual_json_path = f"{report_path}.json"
            
        if not os.path.exists(actual_json_path):
            raise FileNotFoundError(f"Lighthouse report not found at path: {actual_json_path}")
            
        with open(actual_json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @keyword("Run Lighthouse User Flow")
    def run_lighthouse_user_flow(self, user_flow_script, report_output_path="reports/user_flow_report.json"):
        """
        Executes a user flow script (.js or .py) and returns the parsed JSON flow results.
        """
        if not os.path.exists(user_flow_script):
            raise FileNotFoundError(f"User flow script not found: {user_flow_script}")
            
        is_windows = (sys.platform == "win32" or os.name == "nt")
        
        if user_flow_script.endswith(".js"):
            cmd = ["node", user_flow_script]
        elif user_flow_script.endswith(".py"):
            cmd = [sys.executable, user_flow_script]
        else:
            raise ValueError("Supported user flow scripts must be .js or .py files")
            
        print(f"Running user flow script: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, shell=is_windows, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"User flow execution failed: {e.stderr.decode('utf-8', errors='ignore')}")
            
        if not os.path.exists(report_output_path):
            raise FileNotFoundError(f"User flow JSON report not found at: {report_output_path}")
            
        with open(report_output_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ── Inline flow helpers ──────────────────────────────────────────
    # These keywords generate small Node.js scripts on the fly so the
    # user doesn't need to maintain separate .js files for simple
    # warm-load, snapshot, or timespan audits.

    def _run_inline_flow_script(self, script_content, report_json_path):
        """
        Internal helper. Writes a temporary Node.js script, executes it,
        and returns the parsed JSON report it produces.
        """
        report_dir = os.path.dirname(report_json_path) or "reports"
        os.makedirs(report_dir, exist_ok=True)

        tmp_script = os.path.join(report_dir, f"_tmp_flow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.js")
        try:
            with open(tmp_script, "w", encoding="utf-8") as f:
                f.write(script_content)

            is_windows = (sys.platform == "win32" or os.name == "nt")
            result = subprocess.run(
                ["node", tmp_script],
                shell=is_windows, check=True, capture_output=True, text=True
            )
            print(result.stdout)

            if not os.path.exists(report_json_path):
                raise FileNotFoundError(f"Flow report not found at: {report_json_path}")

            with open(report_json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Inline flow script failed: {e.stderr}")
        finally:
            if os.path.exists(tmp_script):
                os.remove(tmp_script)

    @keyword("Run Warm Navigation Audit")
    def run_warm_navigation_audit(self, url, preset="mobile"):
        """
        Runs a cold navigation followed by a warm navigation (disableStorageReset: true)
        to the same URL. Returns the unified flow result containing both steps so cold
        and warm scores can be compared.
        """
        preset_json = json.dumps(preset)
        report_path = os.path.join("reports", "warm_nav_flow.json").replace("\\", "/")
        script = f"""\
const fs = require('fs');
const puppeteer = require('puppeteer');
(async () => {{
  const browser = await puppeteer.launch({{ headless: true, args: ['--no-sandbox', '--disable-gpu'] }});
  try {{
    const page = await browser.newPage();
    const {{ startFlow }} = require('lighthouse');
    const flow = await startFlow(page, {{
      name: 'Cold vs Warm Navigation',
      configContext: {{ settings: {{ preset: {preset_json} }} }},
    }});
    await flow.navigate({json.dumps(url)}, {{ stepName: 'Cold Load (cache cleared)' }});
    await flow.navigate({json.dumps(url)}, {{
      stepName: 'Warm Load (cached)',
      configContext: {{ settings: {{ disableStorageReset: true }} }},
    }});
    const result = await flow.createFlowResult();
    fs.mkdirSync('reports', {{ recursive: true }});
    fs.writeFileSync({json.dumps(report_path)}, JSON.stringify(result, null, 2));
  }} finally {{ await browser.close(); }}
}})();
"""
        return self._run_inline_flow_script(script, report_path)

    @keyword("Run Snapshot Audit")
    def run_snapshot_audit(self, url, interaction_js="", preset="mobile"):
        """
        Navigates to url, optionally runs interaction_js (Puppeteer code executed
        against `page`) to reach a target UI state, then takes a Lighthouse snapshot.

        Snapshot mode audits the current DOM without triggering a navigation, so it
        reports Accessibility, Best Practices, and SEO — but NOT Performance scores.

        Args:
            url: The page URL to navigate to before snapshotting.
            interaction_js: Optional Puppeteer JS code (as a string) that interacts
                with the page after navigation to reach the desired state.
                Example: "await page.click('#open-modal');"
            preset: 'mobile' or 'desktop'.
        """
        preset_json = json.dumps(preset)
        report_path = os.path.join("reports", "snapshot_flow.json").replace("\\", "/")
        interaction_block = interaction_js if interaction_js else "// no interactions"
        script = f"""\
const fs = require('fs');
const puppeteer = require('puppeteer');
(async () => {{
  const browser = await puppeteer.launch({{ headless: true, args: ['--no-sandbox', '--disable-gpu'] }});
  try {{
    const page = await browser.newPage();
    const {{ startFlow }} = require('lighthouse');
    const flow = await startFlow(page, {{
      name: 'Snapshot Audit',
      configContext: {{ settings: {{ preset: {preset_json} }} }},
    }});
    await page.goto({json.dumps(url)}, {{ waitUntil: 'networkidle0' }});
    {interaction_block}
    await flow.snapshot({{ stepName: 'Snapshot — Current Page State' }});
    const result = await flow.createFlowResult();
    fs.mkdirSync('reports', {{ recursive: true }});
    fs.writeFileSync({json.dumps(report_path)}, JSON.stringify(result, null, 2));
  }} finally {{ await browser.close(); }}
}})();
"""
        return self._run_inline_flow_script(script, report_path)

    @keyword("Run Timespan Audit")
    def run_timespan_audit(self, url, interaction_js, preset="mobile"):
        """
        Navigates to url, then opens a Lighthouse timespan measurement window,
        executes interaction_js (Puppeteer code) while metrics are recorded,
        and closes the window.

        Timespan mode captures CLS, TBT, and INP that occur DURING user
        interactions rather than during a page load.

        Args:
            url: The page URL to navigate to before the timespan.
            interaction_js: Puppeteer JS code (as a string) that performs
                interactions while Lighthouse records.
                Example: "await page.evaluate(() => window.scrollBy(0, 2000));"
            preset: 'mobile' or 'desktop'.
        """
        preset_json = json.dumps(preset)
        report_path = os.path.join("reports", "timespan_flow.json").replace("\\", "/")
        script = f"""\
const fs = require('fs');
const puppeteer = require('puppeteer');
(async () => {{
  const browser = await puppeteer.launch({{ headless: true, args: ['--no-sandbox', '--disable-gpu'] }});
  try {{
    const page = await browser.newPage();
    const {{ startFlow }} = require('lighthouse');
    const flow = await startFlow(page, {{
      name: 'Timespan Audit',
      configContext: {{ settings: {{ preset: {preset_json} }} }},
    }});
    await page.goto({json.dumps(url)}, {{ waitUntil: 'networkidle0' }});
    await flow.startTimespan({{ stepName: 'Interaction Timespan' }});
    {interaction_js}
    await flow.endTimespan();
    const result = await flow.createFlowResult();
    fs.mkdirSync('reports', {{ recursive: true }});
    fs.writeFileSync({json.dumps(report_path)}, JSON.stringify(result, null, 2));
  }} finally {{ await browser.close(); }}
}})();
"""
        return self._run_inline_flow_script(script, report_path)

    @keyword("Get Category Score")
    def get_category_score(self, audit_result, category):
        """
        Extracts score for performance/accessibility/seo/best-practices (0 to 100).
        """
        # User flows may contain multiple steps, handle both structures
        if "steps" in audit_result:
            # Average score across steps or get score for the first navigation step
            scores = []
            for step in audit_result["steps"]:
                cat_data = step.get("lhr", {}).get("categories", {}).get(category, {})
                if cat_data.get("score") is not None:
                    scores.append(float(cat_data.get("score")) * 100.0)
            if not scores:
                raise ValueError(f"Category '{category}' not found in any user flow step")
            return sum(scores) / len(scores)

        cat_data = audit_result.get("categories", {}).get(category, {})
        score = cat_data.get("score")
        if score is None:
            raise ValueError(f"Category '{category}' not found in audit results")
        return float(score) * 100.0

    @keyword("Assert Performance Score")
    def assert_performance_score(self, audit_result, min_score):
        """
        Asserts that the performance score is at least the min_score.
        """
        score = self.get_category_score(audit_result, "performance")
        min_score = float(min_score)
        if score < min_score:
            raise AssertionError(f"Performance score {score:.1f} is below minimum threshold of {min_score:.1f}")

    @keyword("Assert Accessibility Score")
    def assert_accessibility_score(self, audit_result, min_score):
        """
        Asserts that the accessibility score is at least the min_score.
        """
        score = self.get_category_score(audit_result, "accessibility")
        min_score = float(min_score)
        if score < min_score:
            raise AssertionError(f"Accessibility score {score:.1f} is below minimum threshold of {min_score:.1f}")

    @keyword("Assert SEO Score")
    def assert_seo_score(self, audit_result, min_score):
        """
        Asserts that the SEO score is at least the min_score.
        """
        score = self.get_category_score(audit_result, "seo")
        min_score = float(min_score)
        if score < min_score:
            raise AssertionError(f"SEO score {score:.1f} is below minimum threshold of {min_score:.1f}")

    @keyword("Extract Core Web Vitals")
    def extract_core_web_vitals(self, audit_result):
        """
        Extracts LCP, FID, CLS, TBT, and Speed Index from audit results.
        Returns a dictionary.
        """
        # If user flow result
        if "steps" in audit_result:
            # Extract from first step containing LHR audits
            audits = {}
            for step in audit_result["steps"]:
                step_audits = step.get("lhr", {}).get("audits", {})
                if step_audits:
                    audits = step_audits
                    break
        else:
            audits = audit_result.get("audits", {})
        
        def val(key):
            return audits.get(key, {}).get("numericValue")

        vitals = {
            "LCP": val("largest-contentful-paint"),
            "FID": val("max-potential-fid"),
            "CLS": val("cumulative-layout-shift"),
            "TBT": val("total-blocking-time"),
            "SI": val("speed-index")
        }
        return vitals

    @keyword("Assert LCP Under Threshold")
    def assert_lcp_under_threshold(self, audit_result, max_ms=2500):
        """
        Asserts that Largest Contentful Paint (LCP) is under the max milliseconds threshold.
        """
        vitals = self.extract_core_web_vitals(audit_result)
        lcp = vitals.get("LCP")
        if lcp is None:
            raise AssertionError("LCP metric not found in audit results")
        max_ms = float(max_ms)
        if lcp > max_ms:
            raise AssertionError(f"LCP is {lcp:.1f} ms, exceeding threshold of {max_ms:.1f} ms")

    @keyword("Assert CLS Under Threshold")
    def assert_cls_under_threshold(self, audit_result, max_value=0.1):
        """
        Asserts that Cumulative Layout Shift (CLS) is under the threshold.
        """
        vitals = self.extract_core_web_vitals(audit_result)
        cls = vitals.get("CLS")
        if cls is None:
            raise AssertionError("CLS metric not found in audit results")
        max_value = float(max_value)
        if cls > max_value:
            raise AssertionError(f"CLS is {cls:.4f}, exceeding threshold of {max_value:.4f}")

    @keyword("Run Batch Audit")
    def run_batch_audit(self, urls_list, preset="mobile"):
        """
        Audits multiple URLs and returns a list of result dictionaries.
        """
        results = []
        for url in urls_list:
            results.append(self.run_lighthouse_audit(url, preset=preset))
        return results
