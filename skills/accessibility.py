"""
accessibility.py — WCAG Accessibility Testing
Uses axe-core via Playwright to check accessibility violations
"""
from playwright.sync_api import Page

AXE_CDN = 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.8.3/axe.min.js'


def inject_axe(page: Page):
    """Inject axe-core into the page."""
    page.add_script_tag(url=AXE_CDN)
    page.wait_for_function('typeof window.axe !== "undefined"', timeout=10000)


def run_axe(page: Page, context=None, options=None) -> dict:
    """
    Run axe accessibility analysis on the current page.
    Returns full axe results including violations, passes, incomplete.
    """
    inject_axe(page)
    axe_call = 'axe.run(document, {})' if not options else f'axe.run(document, {options})'
    results = page.evaluate(f'async () => await {axe_call}')
    return results


def check_accessibility(page: Page, standard='wcag2a') -> dict:
    """
    Run accessibility check and return a structured report.
    Standards: wcag2a, wcag2aa, wcag21a, wcag21aa, wcag22aa
    """
    options = f'{{ runOnly: {{ type: "tag", values: ["{standard}"] }} }}'
    inject_axe(page)
    results = page.evaluate(f'async () => await axe.run(document, {options})')

    violations = results.get('violations', [])
    passes = results.get('passes', [])
    incomplete = results.get('incomplete', [])

    report = {
        'passed': len(violations) == 0,
        'standard': standard,
        'violations': [
            {
                'id': v['id'],
                'impact': v['impact'],
                'description': v['description'],
                'help': v['help'],
                'helpUrl': v['helpUrl'],
                'nodes_count': len(v['nodes']),
                'selectors': [n['target'] for n in v['nodes'][:3]],
            }
            for v in violations
        ],
        'violations_count': len(violations),
        'passes_count': len(passes),
        'incomplete_count': len(incomplete),
    }

    if violations:
        print(f'❌ {len(violations)} accessibility violation(s) found:')
        for v in violations:
            print(f'   [{v["impact"].upper()}] {v["id"]}: {v["help"]}')
    else:
        print(f'✅ No accessibility violations ({standard})')

    return report
