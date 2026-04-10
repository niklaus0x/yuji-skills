"""
core.py — Base Playwright helpers for Yuji
Foundation for all other skill modules
"""
from playwright.sync_api import sync_playwright, Page, Browser
import os
import json
from datetime import datetime

SCREENSHOT_DIR = os.environ.get('YUJI_SCREENSHOT_DIR', '/tmp/yuji-screenshots')
REPORT_DIR = os.environ.get('YUJI_REPORT_DIR', '/tmp/yuji-reports')

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)


def launch_browser(browser_type='chromium', headless=True, **kwargs):
    """Launch a browser instance. Returns (playwright, browser, context, page)."""
    p = sync_playwright().start()
    browser_engine = getattr(p, browser_type)
    browser = browser_engine.launch(headless=headless, **kwargs)
    context = browser.new_context(
        viewport={'width': 1280, 'height': 720},
        user_agent='Yuji-TestBot/1.0 (Playwright)'
    )
    page = context.new_page()
    return p, browser, context, page


def goto(page: Page, url: str, wait_until='networkidle', timeout=30000):
    """Navigate to URL and wait for it to be ready."""
    page.goto(url, wait_until=wait_until, timeout=timeout)
    page.wait_for_load_state('networkidle', timeout=timeout)
    return page


def screenshot(page: Page, name: str, full_page=True) -> str:
    """Take a screenshot and save it. Returns the file path."""
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    path = os.path.join(SCREENSHOT_DIR, f'{name}_{ts}.png')
    page.screenshot(path=path, full_page=full_page)
    print(f'📸 Screenshot: {path}')
    return path


def capture_console_logs(page: Page) -> list:
    """Attach console log listener to page. Returns the log list (mutated live)."""
    logs = []
    page.on('console', lambda msg: logs.append({
        'type': msg.type,
        'text': msg.text,
        'location': msg.location,
    }))
    page.on('pageerror', lambda err: logs.append({
        'type': 'error',
        'text': str(err),
        'location': None,
    }))
    return logs


def get_dom_summary(page: Page) -> dict:
    """Return a summary of interactive elements on the page."""
    return page.evaluate('''
        () => ({
            title: document.title,
            url: location.href,
            buttons: [...document.querySelectorAll('button')].map(b => ({ text: b.innerText.trim(), id: b.id, class: b.className })),
            inputs: [...document.querySelectorAll('input,textarea,select')].map(i => ({ type: i.type, name: i.name, id: i.id, placeholder: i.placeholder })),
            links: [...document.querySelectorAll('a[href]')].slice(0, 20).map(a => ({ text: a.innerText.trim(), href: a.href })),
            headings: [...document.querySelectorAll('h1,h2,h3')].map(h => ({ tag: h.tagName, text: h.innerText.trim() })),
        })
    ''')


def close_all(p, browser):
    """Clean up browser and playwright instance."""
    try:
        browser.close()
        p.stop()
    except Exception:
        pass


def run_test(url: str, test_fn, browser_type='chromium', headless=True, name='test'):
    """
    High-level test runner. Handles launch, navigation, screenshot, and cleanup.
    test_fn receives (page) and should return a dict with 'passed' bool and 'details'.
    """
    p, browser, context, page = launch_browser(browser_type=browser_type, headless=headless)
    logs = capture_console_logs(page)
    result = {'name': name, 'url': url, 'browser': browser_type, 'passed': False, 'details': {}, 'logs': [], 'screenshot': None}
    try:
        goto(page, url)
        test_result = test_fn(page)
        result.update(test_result)
        result['screenshot'] = screenshot(page, name)
    except Exception as e:
        result['error'] = str(e)
        result['screenshot'] = screenshot(page, f'{name}_error')
    finally:
        result['logs'] = logs
        close_all(p, browser)
    status = '✅ PASS' if result.get('passed') else '❌ FAIL'
    print(f'{status} — {name} ({browser_type})')
    return result
