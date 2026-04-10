"""
multi_browser.py — Cross-Browser Testing
Run the same test across Chromium, Firefox, and WebKit (Safari)
"""
from playwright.sync_api import sync_playwright
from typing import Callable

BROWSERS = ['chromium', 'firefox', 'webkit']


def run_cross_browser(url: str, test_fn: Callable, browsers=None, headless=True) -> list:
    """
    Run a test function across multiple browsers.
    test_fn receives (page) and returns a result dict.
    Returns list of results per browser.
    """
    browsers = browsers or BROWSERS
    results = []

    with sync_playwright() as p:
        for browser_name in browsers:
            print(f'\n🌐 Testing on {browser_name}...')
            browser_engine = getattr(p, browser_name)
            browser = browser_engine.launch(headless=headless)
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            page = context.new_page()
            result = {'browser': browser_name, 'url': url, 'passed': False}
            try:
                page.goto(url, wait_until='networkidle', timeout=30000)
                page.wait_for_load_state('networkidle')
                test_result = test_fn(page)
                result.update(test_result)
            except Exception as e:
                result['error'] = str(e)
            finally:
                browser.close()
            status = '✅' if result.get('passed') else '❌'
            print(f'{status} {browser_name}: {result.get("details", result.get("error", ""))}')
            results.append(result)

    passed_count = sum(1 for r in results if r.get('passed'))
    print(f'\n📊 Cross-browser: {passed_count}/{len(browsers)} passed')
    return results


def run_mobile_viewports(url: str, test_fn: Callable, headless=True) -> list:
    """
    Test across common mobile and tablet viewports.
    """
    viewports = [
        {'name': 'Desktop (1280x720)', 'width': 1280, 'height': 720},
        {'name': 'Tablet (768x1024)', 'width': 768, 'height': 1024},
        {'name': 'Mobile L (425x896)', 'width': 425, 'height': 896},
        {'name': 'Mobile S (375x667)', 'width': 375, 'height': 667},
        {'name': 'iPhone SE (320x568)', 'width': 320, 'height': 568},
    ]
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        for vp in viewports:
            context = browser.new_context(viewport={'width': vp['width'], 'height': vp['height']})
            page = context.new_page()
            result = {'viewport': vp['name'], 'url': url, 'passed': False}
            try:
                page.goto(url, wait_until='networkidle', timeout=30000)
                test_result = test_fn(page)
                result.update(test_result)
            except Exception as e:
                result['error'] = str(e)
            finally:
                context.close()
            status = '✅' if result.get('passed') else '❌'
            print(f'{status} {vp["name"]}')
            results.append(result)
        browser.close()

    return results
