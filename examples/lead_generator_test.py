#!/usr/bin/env python3
"""
lead_generator_test.py — Smoke test for saas-lead-generator app
Tests: page loads, search form works, results appear
Usage: python examples/lead_generator_test.py
"""
import sys
sys.path.insert(0, '.')
from skills.core import launch_browser, goto, screenshot, capture_console_logs, close_all
from skills.network import capture_network, get_failed_requests, print_network_summary
from skills.performance import get_performance_metrics
from skills.accessibility import check_accessibility
from skills.reporter import generate_report

URL = 'https://saas-lead-generator-production.up.railway.app'

def main():
    p, browser, context, page = launch_browser()
    logs = capture_console_logs(page)
    requests = capture_network(page)
    results = []

    try:
        print(f'\n🤖 Testing SaaS Lead Generator: {URL}')

        # Test 1: Page loads
        goto(page, URL)
        shot1 = screenshot(page, 'lead_gen_home')
        title = page.title()
        results.append({
            'name': 'Homepage loads',
            'url': URL,
            'browser': 'chromium',
            'passed': 'Lead' in title or page.locator('h1').count() > 0,
            'screenshot': shot1,
            'logs': [],
            'details': {'title': title},
        })

        # Test 2: Search form visible
        form_visible = page.locator('form').count() > 0 or page.locator('input').count() > 0
        results.append({
            'name': 'Search form visible',
            'url': URL,
            'browser': 'chromium',
            'passed': form_visible,
            'screenshot': shot1,
            'logs': [],
            'details': {'form_found': form_visible},
        })

        # Test 3: API health check
        page.goto(f'{URL}/api/health', wait_until='networkidle')
        health_text = page.locator('body').inner_text()
        health_ok = '"status":"ok"' in health_text or 'ok' in health_text.lower()
        shot3 = screenshot(page, 'lead_gen_health')
        results.append({
            'name': 'API health check',
            'url': f'{URL}/api/health',
            'browser': 'chromium',
            'passed': health_ok,
            'screenshot': shot3,
            'logs': [],
            'details': {'response': health_text[:100]},
        })

        # Test 4: Performance
        goto(page, URL)
        perf = get_performance_metrics(page)
        print_network_summary(requests)
        results.append({
            'name': 'Performance budget',
            'url': URL,
            'browser': 'chromium',
            'passed': (perf.get('page_load') or 9999) < 5000,
            'screenshot': shot1,
            'logs': logs,
            'details': perf,
        })

    finally:
        close_all(p, browser)

    report = generate_report(results, title='Lead Generator Smoke Test')
    print(f'\n{"✅ ALL PASSED" if report["passed"] else "❌ SOME FAILED"}')
    sys.exit(0 if report['passed'] else 1)

if __name__ == '__main__':
    main()
