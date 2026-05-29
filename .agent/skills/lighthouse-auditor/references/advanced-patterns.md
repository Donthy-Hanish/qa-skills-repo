# Advanced Lighthouse Automation Patterns

This document covers advanced integration techniques, performance budgeting, device profiles, and long-term trend analysis configurations.

---

## 1. Custom Audits & Configuration File

Lighthouse can be configured using a Javascript or JSON file to customize what categories are audited, change throttling parameters, or run custom plugins.

### Example Custom Configuration (`custom-lh-config.js`)
Create a file named `lh-config.js` to override mobile emulation settings or exclude certain categories:

```javascript
module.exports = {
  extends: 'lighthouse:default',
  settings: {
    // Only run performance and accessibility audits
    onlyCategories: ['performance', 'accessibility'],
    // Use desktop throttling settings rather than default mobile
    throttlingMethod: 'simulate',
    throttling: {
      rttMs: 40,
      throughputKbps: 10 * 1024,
      cpuSlowdownMultiplier: 1,
      requestLatencyMs: 0,
      downloadThroughputKbps: 0,
      uploadThroughputKbps: 0,
    },
    // Emulated screen dimensions
    screenEmulation: {
      mobile: false,
      width: 1350,
      height: 940,
      deviceScaleFactor: 1,
      disabled: false,
    },
  },
};
```

Run Lighthouse with the custom config file:
```bash
npx lighthouse https://example.com --config-path=./lh-config.js
```

---

## 2. Performance Budgets (`budget.json`)

Performance budgets enforce size limits on pages and resource types, ensuring developers don't bloat the application bundle sizes.

### Specifying a Budget File (`budget.json`)
```json
[
  {
    "path": "/*",
    "resourceSizes": [
      {
        "resourceType": "document",
        "budget": 100
      },
      {
        "resourceType": "script",
        "budget": 300
      },
      {
        "resourceType": "image",
        "budget": 500
      },
      {
        "resourceType": "third-party",
        "budget": 200
      }
    ],
    "resourceCounts": [
      {
        "resourceType": "third-party",
        "budget": 10
      }
    ]
  }
]
```

To run Lighthouse with your performance budget:
```bash
npx lighthouse https://example.com --budget-path=./budget.json
```

---

## 3. Multi-Device Testing

QA teams should test both mobile and desktop views to capture varying network profiles and layouts.

### Mobile Audits (Default)
Mobile runs use simulated 3G/4G throttling and screen resolution scaling (representing a Moto G4 by default).
* **CLI Command**: (Standard, default)
  ```bash
  npx lighthouse https://example.com
  ```

### Desktop Audits
Desktop runs bypass standard throttling and use screen resolutions matching a typical desktop display.
* **CLI Command**:
  ```bash
  npx lighthouse https://example.com --preset=desktop
  ```

---

## 4. Trend Tracking & Metrics Analysis

To capture performance trends over time, save the JSON report outputs to an external database (e.g. InfluxDB, PostgreSQL) or run a script that aggregates results into a CSV.

### Example: Storing Score History to CSV
```python
import csv
import os
import json
from datetime import datetime

def log_audit_to_csv(report_json_path, csv_path="reports/audit_trends.csv"):
    with open(report_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    url = data.get("requestedUrl")
    timestamp = data.get("fetchTime")
    
    perf = data["categories"]["performance"]["score"] * 100
    a11y = data["categories"]["accessibility"]["score"] * 100
    best_prac = data["categories"]["best-practices"]["score"] * 100
    seo = data["categories"]["seo"]["score"] * 100
    
    lcp = data["audits"]["largest-contentful-paint"]["numericValue"]
    cls = data["audits"]["cumulative-layout-shift"]["numericValue"]
    
    file_exists = os.path.exists(csv_path)
    
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "URL", "Performance", "Accessibility", "Best Practices", "SEO", "LCP", "CLS"])
        writer.writerow([timestamp, url, perf, a11y, best_prac, seo, lcp, cls])

    print(f"Logged audit results to {csv_path}")
```
Using this method, you can build visual dashboards (e.g., in Grafana or via simple spreadsheet charts) showing how performance scores fluctuate across deployments.
