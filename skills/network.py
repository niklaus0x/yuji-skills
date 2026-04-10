"""
network.py — Network Request Interception & Monitoring
Logs all API calls, detects failed requests, and can mock responses
"""
from playwright.sync_api import Page, Route
from typing import Callable
import json


def capture_network(page: Page) -> list:
    """
    Attach network listener to capture all requests and responses.
    Returns the requests list (mutated live).
    """
    requests = []

    def on_request(request):
        requests.append({
            'url': request.url,
            'method': request.method,
            'resource_type': request.resource_type,
            'status': None,
            'failed': False,
        })

    def on_response(response):
        for r in reversed(requests):
            if r['url'] == response.url:
                r['status'] = response.status
                r['failed'] = response.status >= 400
                break

    def on_request_failed(request):
        for r in reversed(requests):
            if r['url'] == request.url:
                r['failed'] = True
                r['failure'] = request.failure
                break

    page.on('request', on_request)
    page.on('response', on_response)
    page.on('requestfailed', on_request_failed)
    return requests


def get_failed_requests(requests: list) -> list:
    """Filter for failed requests from a captured network log."""
    return [r for r in requests if r.get('failed')]


def get_api_requests(requests: list, path_filter: str = '/api/') -> list:
    """Filter for API requests only."""
    return [r for r in requests if path_filter in r.get('url', '')]


def mock_api(page: Page, url_pattern: str, response_body: dict, status: int = 200):
    """
    Mock an API endpoint to return a specific response.
    url_pattern: glob pattern e.g. '**/api/search-leads'
    """
    def handler(route: Route):
        route.fulfill(
            status=status,
            content_type='application/json',
            body=json.dumps(response_body)
        )
    page.route(url_pattern, handler)
    print(f'🎭 Mocked: {url_pattern} → {status}')


def print_network_summary(requests: list):
    """Print a summary of captured network activity."""
    total = len(requests)
    failed = len(get_failed_requests(requests))
    api_calls = len(get_api_requests(requests))
    status = '✅' if failed == 0 else '❌'
    print(f'{status} Network: {total} requests, {api_calls} API calls, {failed} failed')
    if failed > 0:
        for r in get_failed_requests(requests):
            print(f'   ❌ {r["method"]} {r["url"]} → {r.get("status", "no response")}')
