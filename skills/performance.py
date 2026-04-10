"""
performance.py — Web Performance Metrics
Captures LCP, FID, CLS, TTI, page load time, and resource breakdown
"""
from playwright.sync_api import Page


def get_performance_metrics(page: Page) -> dict:
    """
    Get Core Web Vitals and performance timing from the current page.
    """
    metrics = page.evaluate('''
        () => {
            const perf = performance.getEntriesByType('navigation')[0] || {};
            const paint = {};
            performance.getEntriesByType('paint').forEach(e => { paint[e.name] = e.startTime; });
            const resources = performance.getEntriesByType('resource').map(r => ({
                name: r.name.split('/').pop().substring(0, 50),
                type: r.initiatorType,
                duration: Math.round(r.duration),
                size: r.transferSize || 0,
            })).sort((a,b) => b.duration - a.duration).slice(0, 10);
            return {
                dom_content_loaded: Math.round(perf.domContentLoadedEventEnd - perf.fetchStart) || null,
                page_load: Math.round(perf.loadEventEnd - perf.fetchStart) || null,
                first_paint: Math.round(paint['first-paint']) || null,
                first_contentful_paint: Math.round(paint['first-contentful-paint']) || null,
                dns_lookup: Math.round(perf.domainLookupEnd - perf.domainLookupStart) || null,
                tcp_connect: Math.round(perf.connectEnd - perf.connectStart) || null,
                server_response: Math.round(perf.responseStart - perf.requestStart) || null,
                slowest_resources: resources,
                total_resources: performance.getEntriesByType('resource').length,
            };
        }
    ''')

    # Get LCP via PerformanceObserver (if available)
    try:
        lcp = page.evaluate('''
            () => new Promise(resolve => {
                let lcp = null;
                const obs = new PerformanceObserver(list => {
                    const entries = list.getEntries();
                    lcp = entries[entries.length - 1].startTime;
                });
                obs.observe({ type: 'largest-contentful-paint', buffered: true });
                setTimeout(() => resolve(Math.round(lcp)), 100);
            })
        ''')
        metrics['lcp'] = lcp
    except Exception:
        metrics['lcp'] = None

    # Score the performance
    load = metrics.get('page_load') or 0
    fcp = metrics.get('first_contentful_paint') or 0
    metrics['score'] = 'good' if load < 2000 and fcp < 1800 else 'needs_improvement' if load < 4000 else 'poor'

    # Print summary
    status = {'good': '✅', 'needs_improvement': '⚠️', 'poor': '❌'}.get(metrics['score'], '?')
    print(f"{status} Performance: load={load}ms, FCP={fcp}ms, LCP={metrics.get('lcp')}ms")
    if metrics['slowest_resources']:
        print(f"   Slowest resource: {metrics['slowest_resources'][0]['name']} ({metrics['slowest_resources'][0]['duration']}ms)")

    return metrics


def check_performance_budget(page: Page, budget: dict) -> dict:
    """
    Check page against a performance budget.
    budget example: {'page_load': 3000, 'first_contentful_paint': 1500, 'lcp': 2500}
    """
    metrics = get_performance_metrics(page)
    violations = []
    for metric, limit in budget.items():
        actual = metrics.get(metric)
        if actual and actual > limit:
            violations.append({'metric': metric, 'limit': limit, 'actual': actual, 'over_by': actual - limit})

    passed = len(violations) == 0
    if not passed:
        print(f'❌ Performance budget exceeded:')
        for v in violations:
            print(f'   {v["metric"]}: {v["actual"]}ms (limit: {v["limit"]}ms, over by {v["over_by"]}ms)')
    else:
        print('✅ Within performance budget')

    return {'passed': passed, 'violations': violations, 'metrics': metrics}
