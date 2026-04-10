"""
visual.py — Visual Regression Testing
Compares screenshots against baselines to catch UI regressions
"""
import os
from PIL import Image, ImageChops, ImageDraw
import hashlib
from datetime import datetime

BASELINE_DIR = os.environ.get('YUJI_BASELINE_DIR', '/tmp/yuji-baselines')
DIFF_DIR = os.environ.get('YUJI_DIFF_DIR', '/tmp/yuji-diffs')
os.makedirs(BASELINE_DIR, exist_ok=True)
os.makedirs(DIFF_DIR, exist_ok=True)


def save_baseline(name: str, screenshot_path: str) -> str:
    """Save a screenshot as the baseline for a test."""
    baseline_path = os.path.join(BASELINE_DIR, f'{name}.png')
    img = Image.open(screenshot_path)
    img.save(baseline_path)
    print(f'📐 Baseline saved: {baseline_path}')
    return baseline_path


def compare_to_baseline(name: str, screenshot_path: str, threshold: float = 0.01) -> dict:
    """
    Compare a screenshot to its baseline.
    threshold: max acceptable difference ratio (0.01 = 1%)
    Returns dict with passed, diff_ratio, diff_path.
    """
    baseline_path = os.path.join(BASELINE_DIR, f'{name}.png')
    if not os.path.exists(baseline_path):
        print(f'⚠️  No baseline found for {name} — saving current as baseline')
        save_baseline(name, screenshot_path)
        return {'passed': True, 'diff_ratio': 0.0, 'diff_path': None, 'new_baseline': True}

    baseline = Image.open(baseline_path).convert('RGB')
    current = Image.open(screenshot_path).convert('RGB')

    # Resize if dimensions differ
    if baseline.size != current.size:
        current = current.resize(baseline.size, Image.LANCZOS)

    diff = ImageChops.difference(baseline, current)
    diff_data = list(diff.getdata())
    total_pixels = len(diff_data)
    changed_pixels = sum(1 for pixel in diff_data if any(c > 10 for c in pixel))
    diff_ratio = changed_pixels / total_pixels

    # Save diff image
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    diff_path = os.path.join(DIFF_DIR, f'{name}_diff_{ts}.png')

    # Highlight differences in red
    diff_highlighted = baseline.copy()
    draw = ImageDraw.Draw(diff_highlighted)
    for i, pixel in enumerate(diff_data):
        if any(c > 10 for c in pixel):
            x = i % baseline.width
            y = i // baseline.width
            draw.point((x, y), fill=(255, 0, 0))
    diff_highlighted.save(diff_path)

    passed = diff_ratio <= threshold
    status = '✅' if passed else '❌'
    print(f'{status} Visual diff for {name}: {diff_ratio:.2%} changed (threshold: {threshold:.2%})')
    return {'passed': passed, 'diff_ratio': diff_ratio, 'diff_path': diff_path, 'changed_pixels': changed_pixels, 'total_pixels': total_pixels}


def update_baseline(name: str, screenshot_path: str) -> str:
    """Force update the baseline with a new screenshot."""
    return save_baseline(name, screenshot_path)
