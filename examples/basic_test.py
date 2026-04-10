#!/usr/bin/env python3
"""
basic_test.py — Example: test a running web app
Usage: python examples/basic_test.py --url http://localhost:3000
"""
import sys
sys.path.insert(0, '.')
from skills.core import launch_browser, goto, screenshot, capture_console_logs, get_dom_summary, close_all
from skills.performance import get_performance_metrics
from skills.network import capture_network, print_network_summary
from skills.reporter import generate_report
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='http://localhost:3000', help='URL to test')
    args = parser.parse_args()

    p, browser, context, page = launch_browser()
    logs = capture_console_logs(page)
    requests = capture_network(page)
    results = []

    try:
        print(f'\n🤖 Testing: {args.url}')
        goto(page, args.url)

        # DOM summary
        dom = get_dom_summary(page)
        print(f'📄 Page: "{dom["title"]}" — {len(dom["buttons"])} buttons, {len(dom["inputs"])} inputs')

        # Screenshot
        shot = screenshot(page, 'basic_test')

        # Performance
        perf = get_performance_metrics(page)

        # Network
        print_network_summary(requests)

        # Check basic things are working
        passed = dom['title'] != '' and perf.get('page_load', 9999) < 10000
        results.append({
            'name': 'Basic page load',
            'url': args.url,
            'browser': 'chromium',
            'passed': passed,
            'screenshot': shot,
            'logs': logs,
            'details': {'title': dom['title'], 'load_ms': perf.get('page_load')},
        })

    finally:
        close_all(p, browser)

    report = generate_report(results, title=f'Yuji Test — {args.url}')
    print(f'\n{"✅ PASSED" if report["passed"] else "❌ FAILED"}')
    sys.exit(0 if report['passed'] else 1)

if __name__ == '__main__':
    main()
