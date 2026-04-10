"""
reporter.py — HTML & JSON Test Report Generation
Generates readable reports with screenshots, metrics, and pass/fail status
"""
import json
import os
from datetime import datetime

REPORT_DIR = os.environ.get('YUJI_REPORT_DIR', '/tmp/yuji-reports')
os.makedirs(REPORT_DIR, exist_ok=True)


def generate_report(results: list, title: str = 'Yuji Test Report') -> dict:
    """
    Generate HTML and JSON reports from a list of test results.
    Each result should have: name, passed, url, browser, screenshot, logs, details.
    Returns dict with html_path and json_path.
    """
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    passed = sum(1 for r in results if r.get('passed'))
    failed = len(results) - passed
    overall = passed == len(results)

    # JSON report
    report_data = {
        'title': title,
        'generated_at': datetime.now().isoformat(),
        'summary': {'total': len(results), 'passed': passed, 'failed': failed, 'overall_passed': overall},
        'results': results,
    }
    json_path = os.path.join(REPORT_DIR, f'report_{ts}.json')
    with open(json_path, 'w') as f:
        json.dump(report_data, f, indent=2, default=str)

    # HTML report
    status_badge = '<span style="color:#22c55e">✅ ALL PASSED</span>' if overall else f'<span style="color:#ef4444">❌ {failed} FAILED</span>'
    rows = ''
    for r in results:
        status = '✅' if r.get('passed') else '❌'
        screenshot_html = f'<img src="{r["screenshot"]}" style="max-width:200px;border-radius:4px;" />' if r.get('screenshot') and os.path.exists(r.get('screenshot', '')) else ''
        errors = r.get('error', '')
        logs_html = ''.join([f'<div class="log {l["type"]}">[{l["type"]}] {l["text"]}</div>' for l in r.get('logs', [])[:5]])
        rows += f'''
        <tr>
            <td>{status} {r.get("name", r.get("viewport", r.get("browser", "?")))}</td>
            <td>{r.get("url", "")}</td>
            <td>{r.get("browser", "")}</td>
            <td>{"PASS" if r.get("passed") else "FAIL"}</td>
            <td>{screenshot_html}</td>
            <td><small>{errors}{logs_html}</small></td>
        </tr>'''

    html = f'''<!DOCTYPE html><html><head><title>{title}</title>
<style>body{{font-family:system-ui;background:#0f172a;color:#e2e8f0;padding:2rem}}
table{{width:100%;border-collapse:collapse}}th,td{{padding:.75rem;border-bottom:1px solid #334155;text-align:left}}
th{{background:#1e293b}}tr:hover{{background:#1e293b}}.log.error{{color:#f87171}}.log.warning{{color:#fbbf24}}
.summary{{background:#1e293b;padding:1.5rem;border-radius:.75rem;margin-bottom:2rem}}
</style></head><body>
<h1>🤖 {title}</h1>
<div class="summary">
  <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
  <p>Total: {len(results)} | Passed: {passed} | Failed: {failed}</p>
  <p>{status_badge}</p>
</div>
<table><thead><tr><th>Test</th><th>URL</th><th>Browser</th><th>Status</th><th>Screenshot</th><th>Logs/Errors</th></tr></thead>
<tbody>{rows}</tbody></table>
</body></html>'''

    html_path = os.path.join(REPORT_DIR, f'report_{ts}.html')
    with open(html_path, 'w') as f:
        f.write(html)

    print(f'\n📊 Report: {html_path}')
    print(f'📄 JSON:   {json_path}')
    return {'html_path': html_path, 'json_path': json_path, 'passed': overall, 'summary': report_data['summary']}
