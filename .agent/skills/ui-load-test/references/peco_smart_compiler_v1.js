const fs = require('fs');
const path = require('path');
const readline = require('readline');

// ============================================================================
// PECO SMART HAR COMPILER (V1 - Public API / AI-Search variant)
// ----------------------------------------------------------------------------
// Sibling to qgrid_smart_compiler_v12.js. Designed for projects with:
//   - No login flow (static API key in header for auth, or no auth at all)
//   - AI/vector search endpoints with high latency variance
//   - Multipart form data including file uploads
//
// Auto-detects from the HAR:
//   - API base host  (most-frequent host)
//   - API key header (X-API-Key, Api-Key, Authorization, etc.)
//   - AI-style endpoints (for cost warnings & latency thresholds)
//
// Outputs (same pattern as QGrid v12):
//   - performance/peco_<flow>_smart_load.js   (k6 script)
//   - peco_postprocess.js                     (failure-log enricher)
//   - run-<flow>.ps1                          (Windows one-command wrapper)
//   - Folder layout: hars/  performance/  reports/<flow>/  logs/
//
// Optional inputs:
//   - queries.json  (in project root, array of objects → randomized per iter)
// ============================================================================

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
const askQuestion = (query) => new Promise(resolve => rl.question(query, resolve));

// ----------------------------------------------------------------------------
// Helpers
// ----------------------------------------------------------------------------

function detectApiHost(harEntries) {
    const counts = {};
    for (const entry of harEntries) {
        const req = entry.request;
        if (!req || req.method === 'OPTIONS') continue;
        try {
            const u = new URL(req.url);
            counts[u.origin] = (counts[u.origin] || 0) + 1;
        } catch (_) {}
    }
    const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]);
    return sorted.length ? sorted[0][0] : null;
}

function detectApiPathPrefix(harEntries, host) {
    const counts = {};
    for (const entry of harEntries) {
        const req = entry.request;
        if (!req || req.method === 'OPTIONS' || !req.url.startsWith(host)) continue;
        const pathOnly = req.url.substring(host.length).split('?')[0];
        const m = pathOnly.match(/^(\/api\/v\d+)/i) || pathOnly.match(/^(\/[^/]+\/v\d+)/i);
        if (m) counts[m[1]] = (counts[m[1]] || 0) + 1;
    }
    const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]);
    return sorted.length ? sorted[0][0] : '';
}

function detectApiKey(reqs) {
    const candidates = ['x-api-key', 'api-key', 'apikey', 'authorization'];
    const found = {};
    for (const req of reqs) {
        if (req.method === 'OPTIONS') continue;
        for (const h of (req.headers || [])) {
            const lname = h.name.toLowerCase();
            if (candidates.includes(lname)) {
                if (!found[lname]) found[lname] = { name: h.name, value: h.value, count: 0 };
                found[lname].count++;
            }
        }
    }
    const sorted = Object.values(found).sort((a, b) => b.count - a.count);
    return sorted.length ? sorted[0] : null;
}

function isAiEndpoint(url) {
    return /\/(llm|vector|ai|embed|rag|search|completion|chat)(\b|[-_/])/i.test(url);
}

function parseMultipart(postData) {
    if (!postData) return null;
    if (Array.isArray(postData.params) && postData.params.length > 0) {
        return postData.params.map(p => ({
            name: p.name,
            value: p.value || '',
            fileName: p.fileName || null,
            contentType: p.contentType || null,
        }));
    }
    if (postData.text && /multipart\/form-data/i.test(postData.mimeType || '')) {
        const boundaryMatch = (postData.mimeType || '').match(/boundary=([^;]+)/);
        if (!boundaryMatch) return null;
        const boundary = '--' + boundaryMatch[1].trim().replace(/^['"]|['"]$/g, '');
        const parts = postData.text.split(boundary).slice(1, -1);
        const fields = [];
        for (const rawPart of parts) {
            const part = rawPart.replace(/^\r?\n/, '').replace(/\r?\n$/, '');
            const headerEnd = part.indexOf('\r\n\r\n');
            if (headerEnd === -1) continue;
            const headerBlock = part.substring(0, headerEnd);
            const body = part.substring(headerEnd + 4);
            const nameM = headerBlock.match(/name="([^"]+)"/i);
            const fileM = headerBlock.match(/filename="([^"]+)"/i);
            const ctM = headerBlock.match(/Content-Type:\s*([^\r\n]+)/i);
            if (!nameM) continue;
            fields.push({
                name: nameM[1],
                value: body,
                fileName: fileM ? fileM[1] : null,
                contentType: ctM ? ctM[1].trim() : null,
            });
        }
        return fields.length ? fields : null;
    }
    return null;
}

function parseDurationSec(s) {
    const m = String(s).match(/^(\d+)([smh])?$/);
    if (!m) return 60;
    const n = parseInt(m[1], 10);
    const unit = m[2] || 's';
    return unit === 'h' ? n * 3600 : unit === 'm' ? n * 60 : n;
}

function buildThresholds(calls) {
    const aiAny = calls.some(c => isAiEndpoint(c.url));
    const obj = {
        'http_req_failed':   "['rate<0.05']",
        'http_req_duration': aiAny ? "['p(95)<10000']" : "['p(95)<2000']",
    };
    return '{ ' + Object.entries(obj).map(([k, v]) => `'${k}': ${v}`).join(', ') + ' }';
}

function emitMultipart(cleanUrl, method, stepLabel, fields) {
    let s = `        {\n`;
    s += `            const _url = \`${cleanUrl}\`;\n`;
    s += `            const _form = {};\n`;
    for (const f of fields) {
        const safeName = JSON.stringify(f.name);
        if (f.fileName || /^application\/(json|octet-stream)|^text\/|^image\//.test(f.contentType || '')) {
            const fileName = JSON.stringify(f.fileName || (f.name + '.dat'));
            const ct = JSON.stringify(f.contentType || 'application/octet-stream');
            s += `            _form[${safeName}] = (queryOverride && queryOverride[${safeName}] !== undefined) ? http.file(String(queryOverride[${safeName}]), ${fileName}, ${ct}) : http.file(${JSON.stringify(f.value)}, ${fileName}, ${ct});\n`;
        } else {
            s += `            _form[${safeName}] = (queryOverride && queryOverride[${safeName}] !== undefined) ? String(queryOverride[${safeName}]) : ${JSON.stringify(f.value)};\n`;
        }
    }
    s += `            const _hdrs = buildAuthHeaders();\n`;
    s += `            res = http.${method.toLowerCase()}(_url, _form, _hdrs);\n`;
    s += `            checkAndLog('${stepLabel}', { method:'${method}', url:_url, headers:_hdrs.headers, body:_form }, res);\n`;
    s += `        }\n\n`;
    return s;
}

// ----------------------------------------------------------------------------
// Compile
// ----------------------------------------------------------------------------

async function compile(harFilePath, vus, execMode, execValue, sleepSec) {
    console.log(`\n🚀 Booting PECO Smart Compiler V1...`);

    const rawHarPath = path.resolve(harFilePath);
    if (!fs.existsSync(rawHarPath)) {
        console.error(`❌ ERROR: Could not find HAR file at ${rawHarPath}`);
        return;
    }

    const flowName = path.basename(harFilePath, '.har').replace(/^peco_/, '');

    const HARS_DIR = path.join(__dirname, 'hars');
    const PERF_DIR = path.join(__dirname, 'performance');
    const REPORTS_DIR = path.join(__dirname, 'reports');
    const FLOW_REPORT_DIR = path.join(REPORTS_DIR, flowName);
    const LOGS_DIR = path.join(__dirname, 'logs');
    [HARS_DIR, PERF_DIR, REPORTS_DIR, FLOW_REPORT_DIR, LOGS_DIR].forEach(dir => {
        if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    });

    if (path.dirname(rawHarPath) === __dirname) {
        const target = path.join(HARS_DIR, path.basename(rawHarPath));
        if (!fs.existsSync(target)) {
            try { fs.copyFileSync(rawHarPath, target); console.log(`📦 Copied HAR into hars/`); } catch (_) {}
        }
    }

    const OUTPUT_FILE = path.join(PERF_DIR, `peco_${flowName}_smart_load.js`);
    const flowReportDirRel = path.relative(__dirname, FLOW_REPORT_DIR).replace(/\\/g, '/');

    const har = JSON.parse(fs.readFileSync(rawHarPath, 'utf8'));
    const allEntries = har.log.entries || [];
    console.log(`🔍 Scanning HAR (${allEntries.length} total entries)...`);

    const host = detectApiHost(allEntries);
    if (!host) {
        console.error(`❌ ERROR: Could not detect any API host from HAR. Is the HAR empty?`);
        return;
    }
    const pathPrefix = detectApiPathPrefix(allEntries, host);
    const baseUrl = host + pathPrefix;
    console.log(`🌐 Detected API base: ${baseUrl}`);

    const apiCalls = allEntries
        .map(e => e.request)
        .filter(req => req && req.url && req.url.startsWith(host) && req.method !== 'OPTIONS');

    const dynamicCalls = apiCalls.filter(req => {
        const pathOnly = req.url.substring(host.length).split('?')[0];
        return !/\.(js|css|png|jpe?g|svg|gif|ico|woff2?|ttf|map)$/i.test(pathOnly);
    });
    console.log(`✂️  Stripped static assets. Found ${dynamicCalls.length} pure API calls.`);

    if (dynamicCalls.length === 0) {
        console.error(`❌ ERROR: No API calls found after filtering. Is the HAR for the right domain?`);
        return;
    }

    const apiKey = detectApiKey(dynamicCalls);
    if (apiKey) console.log(`🔑 Detected auth header: ${apiKey.name} (used ${apiKey.count}x)`);
    else console.log(`🔓 No auth header detected — assuming fully public API`);

    const aiCalls = dynamicCalls.filter(req => isAiEndpoint(req.url));
    if (aiCalls.length > 0) {
        const approxIters = execMode === 'duration'
            ? Math.round(parseDurationSec(execValue) / Math.max(sleepSec, 1)) * vus
            : vus * parseInt(execValue, 10);
        const approxAiHits = aiCalls.length * approxIters;
        console.log('');
        console.log('⚠️  AI/vector/search endpoints detected:');
        for (const c of aiCalls) console.log(`     • ${c.method} ${c.url.substring(host.length).split('?')[0]}`);
        console.log(`   Estimated AI requests this run: ~${approxAiHits.toLocaleString()}`);
        console.log(`   At ~$0.001-$0.01 per LLM call, that's roughly $${(approxAiHits * 0.001).toFixed(2)}-$${(approxAiHits * 0.01).toFixed(2)} of backend cost.`);
        console.log(`   Adjust VUs / duration / sleep if this is more than you intended.`);
        console.log('');
    }

    const optionsBlock = execMode === 'duration'
        ? `export const options = {\n    vus: ${vus},\n    duration: '${execValue}',\n    thresholds: ${buildThresholds(dynamicCalls)},\n};`
        : `export const options = {\n    scenarios: { per_vu_scenario: { executor: 'per-vu-iterations', vus: ${vus}, iterations: ${execValue}, maxDuration: '2h' } },\n    thresholds: ${buildThresholds(dynamicCalls)},\n};`;

    let k6 = `import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { SharedArray } from 'k6/data';
import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.1/index.js";

// Optional query pool: if queries.json exists, the script will randomize per
// iteration. Otherwise it uses values captured in the HAR.
const queryPool = new SharedArray('queries', function () {
    try { return JSON.parse(open('../queries.json')); } catch (e) { return []; }
});

${optionsBlock}

const BASE_URL = '${baseUrl}';
${apiKey ? `const API_KEY_HEADER_NAME = ${JSON.stringify(apiKey.name)};\nconst API_KEY_VALUE = ${JSON.stringify(apiKey.value)};` : '// No API key auth detected'}
const SLEEP_BETWEEN_ITER = ${sleepSec};

const FAILURE_BEGIN_MARK = '__PECO_FAILURE_BEGIN__';
const FAILURE_END_MARK   = '__PECO_FAILURE_END__';

let vuFailureCount = 0;

function logFailure(stepName, req, res, extra) {
    try {
        const entry = {
            vu: __VU, iter: __ITER, step: stepName,
            timestamp: new Date().toISOString(),
            request: {
                method: req.method || 'GET',
                url: req.url,
                headers: req.headers || {},
                body: req.body || null,
            },
            response: {
                status: res.status,
                statusText: res.status_text || '',
                headers: res.headers || {},
                body: (res.body && res.body.length > 8000) ? res.body.substring(0, 8000) + '...[truncated]' : res.body,
            },
            extra: extra || null,
        };
        console.log(FAILURE_BEGIN_MARK + JSON.stringify(entry) + FAILURE_END_MARK);
        vuFailureCount++;
    } catch (e) {}
}

function checkAndLog(stepName, req, res, expectedStatuses) {
    const expected = expectedStatuses || [200, 201, 204];
    const ok = expected.indexOf(res.status) !== -1;
    const checkObj = {};
    checkObj[stepName + ' OK'] = () => ok;
    check(res, checkObj);
    if (!ok) {
        logFailure(stepName, req, res);
        console.error(\`❌ VU \${__VU} iter \${__ITER} - \${stepName} FAILED. Status=\${res.status}\`);
    }
    return ok;
}

let vuAnnounced = false;
function announceVu() {
    if (vuAnnounced) return;
    vuAnnounced = true;
    console.log(\`▶️  VU \${__VU} starting flow\`);
}

function pickQuery() {
    if (!queryPool || queryPool.length === 0) return null;
    const idx = ((__VU - 1) * 7919 + __ITER) % queryPool.length;
    return queryPool[idx];
}

function buildAuthHeaders(extra) {
    const h = Object.assign({
        'Accept': 'application/json, text/plain, */*'${apiKey ? ',\n        [API_KEY_HEADER_NAME]: API_KEY_VALUE' : ''}
    }, extra || {});
    return { headers: h };
}

export default function main() {
    announceVu();
    let res;
    let reqHeaders;
    const queryOverride = pickQuery();

    group('PECO API Flow', function () {
`;

    for (const req of dynamicCalls) {
        const cleanUrl = req.url.replace(baseUrl, '${BASE_URL}').replace(/`/g, '\\`');
        const pathOnly = req.url.substring(host.length).split('?')[0];
        const endpointName = (pathOnly.split('/').filter(Boolean).pop() || 'endpoint').replace(/['"\\]/g, '');
        const stepLabel = `${req.method} ${endpointName}`;

        if (req.method === 'GET') {
            k6 += `        {\n`;
            k6 += `            const _url = \`${cleanUrl}\`;\n`;
            k6 += `            const _hdrs = buildAuthHeaders();\n`;
            k6 += `            res = http.get(_url, _hdrs);\n`;
            k6 += `            checkAndLog('${stepLabel}', { method:'GET', url:_url, headers:_hdrs.headers, body:null }, res);\n`;
            k6 += `        }\n\n`;
            continue;
        }

        const multipart = parseMultipart(req.postData);
        if (multipart) {
            k6 += emitMultipart(cleanUrl, req.method, stepLabel, multipart);
            continue;
        }

        const rawBody = (req.postData && req.postData.text) ? req.postData.text : '{}';
        const bodyLiteral = JSON.stringify(rawBody);
        k6 += `        {\n`;
        k6 += `            const _url = \`${cleanUrl}\`;\n`;
        k6 += `            const _body = ${bodyLiteral};\n`;
        k6 += `            const _hdrs = buildAuthHeaders({ 'Content-Type': 'application/json' });\n`;
        k6 += `            res = http.${req.method.toLowerCase()}(_url, _body, _hdrs);\n`;
        k6 += `            checkAndLog('${stepLabel}', { method:'${req.method}', url:_url, headers:_hdrs.headers, body:_body }, res);\n`;
        k6 += `        }\n\n`;
    }

    k6 += `    });
    sleep(SLEEP_BETWEEN_ITER);
}

const RUN_TIMESTAMP = (function () {
    const d = new Date();
    const pad = (n) => String(n).padStart(2, '0');
    return d.getFullYear() + '-' + pad(d.getMonth()+1) + '-' + pad(d.getDate())
         + '_' + pad(d.getHours()) + '-' + pad(d.getMinutes()) + '-' + pad(d.getSeconds());
})();
const RUN_LABEL = '${flowName}__' + RUN_TIMESTAMP;
const REPORT_DIR_REL = '${flowReportDirRel}';

function buildRunMetadataBanner(data) {
    const m = data.metrics || {};
    const v = (metric, key) => (m[metric] && m[metric].values && m[metric].values[key]) || 0;

    const totalReqs   = v('http_reqs', 'count');
    const failRate    = v('http_req_failed', 'rate');
    const failPct     = (failRate * 100).toFixed(2) + '%';
    const iterations  = v('iterations', 'count');
    const vusMax      = v('vus_max', 'max');

    // User-flow timings (the headline numbers — what each user actually waited)
    const flowMed     = v('group_duration', 'med');
    const flowP95     = v('group_duration', 'p(95)');

    // Per-request timing (secondary, useful for backend diagnostics)
    const reqMed      = v('http_req_duration', 'med');
    const reqP95      = v('http_req_duration', 'p(95)');

    // Format ms nicely: under 1000ms show ms, over show seconds
    const fmt = (ms) => ms >= 1000 ? (ms / 1000).toFixed(2) + ' s' : Math.round(ms) + ' ms';

    return \`
    <style>
      .peco-runmeta { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 20px; padding: 16px 20px; border-left: 4px solid #2e7d32; background: #e8f5e9; border-radius: 4px; }
      .peco-runmeta h3 { margin: 0 0 10px 0; color: #1b5e20; font-size: 16px; }
      .peco-runmeta h4 { margin: 14px 0 6px 0; color: #2e7d32; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #c8e6c9; padding-bottom: 3px; }
      .peco-runmeta table { border-collapse: collapse; width: auto; }
      .peco-runmeta td { padding: 3px 14px 3px 0; font-size: 13px; vertical-align: top; }
      .peco-runmeta td.label { color: #555; font-weight: 600; min-width: 220px; }
      .peco-runmeta td.val { color: #111; font-family: ui-monospace, "SF Mono", Consolas, monospace; min-width: 110px; }
      .peco-runmeta td.hint { color: #666; font-size: 12px; font-style: italic; }
      .peco-runmeta .headline { color: #1b5e20; font-weight: 700; font-size: 14px; }
    </style>
    <div class="peco-runmeta">
      <h3>📋 Run Metadata</h3>

      <h4>Run setup</h4>
      <table>
        <tr><td class="label">Flow:</td><td class="val">${flowName}</td><td class="hint"></td></tr>
        <tr><td class="label">Run started:</td><td class="val">\` + RUN_TIMESTAMP + \`</td><td class="hint"></td></tr>
        <tr><td class="label">Concurrent users (VUs):</td><td class="val">\` + vusMax + \`</td><td class="hint">simulated users running in parallel</td></tr>
        <tr><td class="label">User flows completed:</td><td class="val">\` + iterations + \`</td><td class="hint">end-to-end iterations finished</td></tr>
        <tr><td class="label">Total HTTP requests made:</td><td class="val">\` + totalReqs + \`</td><td class="hint">individual API calls across all flows</td></tr>
      </table>

      <h4>User experience (headline)</h4>
      <table>
        <tr><td class="label">HTTP failure rate:</td><td class="val">\` + failPct + \`</td><td class="hint">% of API calls that did not return success</td></tr>
        <tr><td class="label">Typical user-flow duration:</td><td class="val headline">\` + fmt(flowMed) + \`</td><td class="hint">median time for one full flow (50% faster, 50% slower)</td></tr>
        <tr><td class="label">Slowest 5% of user-flows took:</td><td class="val headline">\` + fmt(flowP95) + \`</td><td class="hint">p(95) — 95% of users finished within this</td></tr>
      </table>

      <h4>Backend diagnostics (per single API call)</h4>
      <table>
        <tr><td class="label">Typical single-call latency:</td><td class="val">\` + fmt(reqMed) + \`</td><td class="hint">median of individual http_req_duration</td></tr>
        <tr><td class="label">Slowest 5% of single calls took:</td><td class="val">\` + fmt(reqP95) + \`</td><td class="hint">p(95) of http_req_duration — useful for spotting slow endpoints</td></tr>
      </table>
    </div>\`;
}

export function handleSummary(data) {
    const baseHtml = htmlReport(data);
    const runMetaHtml = buildRunMetadataBanner(data);

    let enriched = baseHtml;
    if (enriched.indexOf('<body>') !== -1) enriched = enriched.replace('<body>', '<body>' + runMetaHtml);
    else enriched = runMetaHtml + enriched;

    const placeholder = '<!--PECO_FAILURES_PLACEHOLDER-->';
    if (enriched.indexOf('</body>') !== -1) enriched = enriched.replace('</body>', placeholder + '</body>');
    else enriched = enriched + placeholder;

    const htmlPath = REPORT_DIR_REL + '/' + RUN_LABEL + '_report.html';
    const out = {};
    out[htmlPath] = enriched;
    out.stdout = textSummary(data, { indent: " ", enableColors: true })
               + '\\n\\n📄 Base report: ' + htmlPath
               + '\\n   (Post-processor will enrich with failure details if any failures occurred)\\n';
    return out;
}
`;

    fs.writeFileSync(OUTPUT_FILE, k6);

    let scriptValidated = false;
    try {
        require('child_process').execSync(`node --check "${OUTPUT_FILE}"`, { stdio: 'pipe' });
        scriptValidated = true;
    } catch (e) {
        const msg = e.stderr ? e.stderr.toString() : e.message;
        console.error(`\n⚠️  WARNING: Generated script failed Node syntax check.\n${msg}\n`);
    }

    const POSTPROC_FILE = path.join(__dirname, 'peco_postprocess.js');
    fs.writeFileSync(POSTPROC_FILE, getPostProcessorSource());

    const PS_WRAPPER = path.join(__dirname, `run-${flowName}.ps1`);
    const psBody = `# Auto-generated wrapper for ${flowName} (PECO)
# Runs k6, captures stdout/stderr, then post-processes the HTML report.

$ErrorActionPreference = "Continue"

try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding = [System.Text.Encoding]::UTF8
} catch { }

$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

$LogDir = Join-Path $ProjectRoot "logs"
if (!(Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }

$Timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$LogFile = Join-Path $LogDir "k6_run_${flowName}_$Timestamp.log"

Write-Host ""
Write-Host "[PECO] Running k6 load test for ${flowName}..." -ForegroundColor Cyan
Write-Host "       Log file: $LogFile" -ForegroundColor Gray
Write-Host ""

cmd /c "k6 run ""${path.relative(__dirname, OUTPUT_FILE).replace(/\\/g, '/')}"" 2>&1" | Tee-Object -FilePath $LogFile
$K6Exit = $LASTEXITCODE

if ($K6Exit -ne 0 -and $K6Exit -ne 99) {
    Write-Host "[PECO] WARNING: k6 exited with code $K6Exit (continuing to post-process)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[PECO] Post-processing run log to enrich HTML report..." -ForegroundColor Cyan
& node "peco_postprocess.js" "$LogFile" "${flowName}"

if ($LASTEXITCODE -eq 0) {
    Write-Host "[PECO] Done." -ForegroundColor Green
} else {
    Write-Host "[PECO] ERROR: Post-processor failed with code $LASTEXITCODE" -ForegroundColor Red
}
`;
    const bom = Buffer.from([0xEF, 0xBB, 0xBF]);
    fs.writeFileSync(PS_WRAPPER, Buffer.concat([bom, Buffer.from(psBody, 'utf8')]));

    console.log(`✅ Smart Compilation Complete!${scriptValidated ? '  (script syntax verified)' : ''}`);
    console.log(`   📁 k6 Script:      ${OUTPUT_FILE}`);
    console.log(`   📁 PowerShell run: ${PS_WRAPPER}`);
    console.log(`   📁 Reports:        ${FLOW_REPORT_DIR}${path.sep}  (timestamped per run)`);
    console.log(``);
    console.log(`👉 To execute the test:`);
    console.log(`     .\\${path.basename(PS_WRAPPER)}`);
    console.log(``);
    console.log(`💡 TIP: For realistic AI-search load testing, create a queries.json in your project root.`);
    console.log(`   Each iteration will pick a different entry, defeating LLM response caching.`);
    console.log(`   Example:`);
    console.log(`     [{"userQuery":"...","lat":0,"lng":0}, {"userQuery":"...","lat":34.05,"lng":-118.25}]`);
    console.log(``);
}

// ----------------------------------------------------------------------------
// Post-processor source
// ----------------------------------------------------------------------------
function getPostProcessorSource() {
    return `// PECO run post-processor: parses failure markers from k6 stdout log,
// enriches the matching HTML report with a Failure Diagnostics section.
// Usage: node peco_postprocess.js <log_file> <flow_name>

const fs = require('fs');
const path = require('path');

const FAILURE_BEGIN_MARK = '__PECO_FAILURE_BEGIN__';
const FAILURE_END_MARK   = '__PECO_FAILURE_END__';
const PLACEHOLDER        = '<!--PECO_FAILURES_PLACEHOLDER-->';
const SAMPLES_PER_GROUP  = 10;

function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    if (typeof str !== 'string') str = JSON.stringify(str, null, 2);
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function extractFailures(logText) {
    const out = [];
    let cursor = 0;
    while (true) {
        const begin = logText.indexOf(FAILURE_BEGIN_MARK, cursor);
        if (begin === -1) break;
        const end = logText.indexOf(FAILURE_END_MARK, begin);
        if (end === -1) break;
        try { out.push(JSON.parse(logText.substring(begin + FAILURE_BEGIN_MARK.length, end))); } catch (e) {}
        cursor = end + FAILURE_END_MARK.length;
    }
    return out;
}

function groupFailures(failures) {
    const groups = new Map();
    for (const f of failures) {
        const key = (f.step || 'unknown') + ' :: HTTP ' + (f.response ? f.response.status : '?');
        if (!groups.has(key)) groups.set(key, { key, count: 0, samples: [] });
        const g = groups.get(key);
        g.count++;
        if (g.samples.length < SAMPLES_PER_GROUP) g.samples.push(f);
    }
    return Array.from(groups.values()).sort((a, b) => b.count - a.count);
}

function buildFailuresHtml(failures) {
    const total = failures.length;
    const style = \`
    <style>
      .peco-failures { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px 20px; padding: 20px; border: 2px solid #d9534f; border-radius: 8px; background: #fff9f9; }
      .peco-failures h2 { color: #d9534f; margin-top: 0; }
      .peco-failures .count-badge { display:inline-block; background:#d9534f; color:#fff; padding:2px 10px; border-radius:12px; font-size:13px; margin-left:8px; }
      .peco-group { border: 1px solid #ccc; border-radius: 6px; margin: 14px 0; background: #fff; }
      .peco-group > summary { cursor: pointer; padding: 10px 14px; font-weight: 600; background: #ffe4e4; border-radius: 6px; }
      .peco-failure { border: 1px solid #e0e0e0; border-radius: 6px; margin: 10px 0; background: #fafafa; }
      .peco-failure summary { cursor: pointer; padding: 8px 12px; font-weight: 500; font-size: 13px; }
      .peco-failure .body { padding: 10px 14px; }
      .peco-meta span { display: inline-block; margin-right: 14px; font-size: 12px; color: #555; }
      .peco-section h4 { margin: 4px 0; color: #333; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
      .peco-section pre { background: #f4f4f4; padding: 10px; border-radius: 4px; overflow-x: auto; font-size: 12px; white-space: pre-wrap; word-break: break-word; max-height: 280px; overflow-y: auto; }
      .peco-no-failures { color: #2e7d32; font-weight: 600; padding: 10px; background: #e8f5e9; border-radius: 6px; }
      .peco-truncated-note { font-size: 12px; color: #856404; background: #fff3cd; padding: 6px 10px; border-radius: 4px; margin: 6px 0; }
    </style>\`;

    if (total === 0) return style + '<div class="peco-failures"><h2>Failure Diagnostics</h2><div class="peco-no-failures">✅ No failed requests captured during this run.</div></div>';

    const groups = groupFailures(failures);
    let html = '';
    let gi = 0;
    for (const g of groups) {
        gi++;
        const truncated = g.count > g.samples.length;
        let samples = '';
        for (let i = 0; i < g.samples.length; i++) {
            const f = g.samples[i];
            samples += \`<details class="peco-failure"><summary>Sample \${i+1} • VU \${f.vu} / iter \${f.iter} • \${escapeHtml(f.timestamp)}</summary>
              <div class="body">
                <div class="peco-meta"><span><b>Method:</b> \${escapeHtml(f.request.method)}</span><span><b>URL:</b> \${escapeHtml(f.request.url)}</span><span><b>Status:</b> \${f.response.status}</span></div>
                <div class="peco-section"><h4>Request Headers</h4><pre>\${escapeHtml(f.request.headers)}</pre></div>
                <div class="peco-section"><h4>Request Body</h4><pre>\${escapeHtml(f.request.body)}</pre></div>
                <div class="peco-section"><h4>Response Headers</h4><pre>\${escapeHtml(f.response.headers)}</pre></div>
                <div class="peco-section"><h4>Response Body</h4><pre>\${escapeHtml(f.response.body)}</pre></div>
                \${f.extra ? '<div class="peco-section"><h4>Notes</h4><pre>' + escapeHtml(f.extra) + '</pre></div>' : ''}
              </div></details>\`;
        }
        html += \`<details class="peco-group" \${gi === 1 ? 'open' : ''}><summary>\${escapeHtml(g.key)} — \${g.count} failure\${g.count > 1 ? 's' : ''}</summary><div class="group-body">\${truncated ? '<div class="peco-truncated-note">Showing ' + g.samples.length + ' of ' + g.count + ' failures of this type.</div>' : ''}\${samples}</div></details>\`;
    }
    return style + '<div class="peco-failures"><h2>Failure Diagnostics <span class="count-badge">' + total + ' total / ' + groups.length + ' types</span></h2>' + html + '</div>';
}

function findLatestReport(flowName) {
    const dir = path.join(__dirname, 'reports', flowName);
    if (!fs.existsSync(dir)) return null;
    const files = fs.readdirSync(dir).filter(f => f.endsWith('_report.html'))
        .map(f => ({ full: path.join(dir, f), mtime: fs.statSync(path.join(dir, f)).mtimeMs }))
        .sort((a, b) => b.mtime - a.mtime);
    return files.length ? files[0].full : null;
}

function main() {
    const logFile  = process.argv[2];
    const flowName = process.argv[3];
    if (!logFile || !flowName) { console.error('Usage: node peco_postprocess.js <log_file> <flow_name>'); process.exit(2); }
    if (!fs.existsSync(logFile)) { console.error('Log file not found:', logFile); process.exit(2); }

    const failures = extractFailures(fs.readFileSync(logFile, 'utf8'));
    console.log('   Failures parsed from log: ' + failures.length);

    const reportFile = findLatestReport(flowName);
    if (!reportFile) { console.error('   No HTML report found in reports/' + flowName + '/'); process.exit(1); }
    console.log('   Enriching report: ' + reportFile);

    let html = fs.readFileSync(reportFile, 'utf8');
    const failuresHtml = buildFailuresHtml(failures);

    const existing = html.match(/<style>\\s*\\.peco-failures[\\s\\S]*?<\\/div>\\s*(?=<\\/body>|$)/);
    if (existing) html = html.replace(existing[0], '');

    if (html.indexOf(PLACEHOLDER) !== -1) html = html.replace(PLACEHOLDER, failuresHtml);
    else if (html.indexOf('</body>') !== -1) html = html.replace('</body>', failuresHtml + '</body>');
    else html = html + failuresHtml;

    fs.writeFileSync(reportFile, html);
    const jsonFile = reportFile.replace(/_report\\.html$/, '_failures.json');
    fs.writeFileSync(jsonFile, JSON.stringify(failures, null, 2));

    console.log('   Report enriched.');
    console.log('   Open: ' + reportFile);
    if (failures.length > 0) console.log('   Failures JSON: ' + jsonFile);
}

main();
`;
}

// ----------------------------------------------------------------------------
// CLI
// ----------------------------------------------------------------------------

async function startGenerator() {
    console.log("=========================================");
    console.log("🚀 PECO Smart Performance Compiler V1");
    console.log("    (Public API / AI-search variant)");
    console.log("=========================================");

    const captureFile = await askQuestion('📂 Enter path to your HAR file: ');
    const vus = await askQuestion('👥 Enter number of concurrent users: ');

    console.log('\n⚙️  Choose Execution Mode:');
    console.log('   1. By Duration');
    console.log('   2. By Runs Per User');
    const modeChoice = await askQuestion('Enter your choice (1 or 2): ');

    const execMode = modeChoice === '2' ? 'iterations' : 'duration';
    const execValue = await askQuestion(execMode === 'iterations' ? '🔄 Runs per user: ' : '⏱️  Duration (e.g. 2m): ');

    const sleepInput = await askQuestion('💤 Sleep seconds between iterations [default 2]: ');
    const sleepSec = parseInt(sleepInput, 10) || 2;

    await compile(captureFile, parseInt(vus, 10), execMode, execValue, sleepSec);
    rl.close();
}

startGenerator();
