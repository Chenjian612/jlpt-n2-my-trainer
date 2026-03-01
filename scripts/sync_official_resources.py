#!/usr/bin/env python3
"""Sync official JLPT resources into local skill storage.

Outputs under references/official:
- pages/: crawled html pages
- files/: downloaded pdf/mp3/zip attachments
- meta/: manifests and indexes
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlsplit

DEFAULT_SOURCES = [
    'https://www.jlpt.jp/e/guideline/testsections.html',
    'https://www.jlpt.jp/e/guideline/results.html',
    'https://www.jlpt.jp/e/samples/forlearners.html',
    'https://www.jlpt.jp/e/samples/sampleindex.html',
    'https://www.jlpt.jp/e/samples/sample09.html',
    'https://www.jlpt.jp/e/reference/forteachers.html',
    'https://www.jlpt.jp/e/topics/202401191708325175.html',
    'https://info.jees-jlpt.jp/info/2026-1jisshiannai.html',
    'https://www.jlpt.jp/e/application/overseas_index.html',
]
ALLOWED_HOSTS = {'www.jlpt.jp', 'jlpt.jp', 'info.jees-jlpt.jp'}
ATT_EXTS = ('.pdf', '.mp3', '.zip')


def run_curl_text(url: str, timeout: int) -> tuple[str | None, str | None]:
    cmd = ['curl', '-LfsS', '--retry', '2', '--max-time', str(timeout), url]
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode != 0:
        return None, (p.stderr.decode('utf-8', errors='ignore').strip() or 'curl failed')
    return p.stdout.decode('utf-8', errors='ignore'), None


def run_curl_file(url: str, out: Path, timeout: int) -> tuple[bool, str]:
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ['curl', '-LfsS', '--retry', '2', '--max-time', str(timeout), url, '-o', str(out)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode == 0, (p.stderr or '').strip()


def extract_links(html_text: str) -> list[str]:
    return re.findall(r'href=["\']([^"\']+)["\']', html_text, flags=re.IGNORECASE)


def safe_page_name(url: str, prefix: str) -> str:
    sp = urlsplit(url)
    slug = (sp.netloc + sp.path).strip('/').replace('/', '_')
    slug = re.sub(r'[^A-Za-z0-9._-]+', '_', slug)
    if not slug.endswith('.html'):
        slug += '.html'
    return f'{prefix}_{slug}'


def safe_file_name(url: str) -> str:
    sp = urlsplit(url)
    base = Path(sp.path).name or 'download.bin'
    base = re.sub(r'[^A-Za-z0-9._-]+', '_', base)
    digest = hashlib.md5(url.encode('utf-8')).hexdigest()[:10]
    return f'{digest}_{base}'


def save_json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')


def build_indexes(meta_dir: Path, file_manifest: list[dict]) -> None:
    n2_manifest = [
        r for r in file_manifest
        if 'n2' in r.get('url', '').lower() or 'n2' in Path(r.get('file', '')).name.lower()
    ]
    save_json(meta_dir / 'n2_manifest.json', n2_manifest)

    with (meta_dir / 'n2_index.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['source_url', 'local_file', 'bytes'])
        for r in n2_manifest:
            w.writerow([r.get('url', ''), r.get('file', ''), r.get('bytes', 0)])

    by_ext: dict[str, int] = {}
    for r in file_manifest:
        ext = Path(r.get('file', '')).suffix.lower() or 'unknown'
        by_ext[ext] = by_ext.get(ext, 0) + 1

    save_json(meta_dir / 'summary.json', {
        'total_files': len(file_manifest),
        'n2_files': len(n2_manifest),
        'by_ext': by_ext,
    })


def main() -> int:
    parser = argparse.ArgumentParser(description='Sync official JLPT resources to local skill folder')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent.parent / 'references' / 'official')
    parser.add_argument('--page-timeout', type=int, default=45)
    parser.add_argument('--file-timeout', type=int, default=60)
    parser.add_argument('--max-child-pages', type=int, default=160)
    args = parser.parse_args()

    root = args.root
    pages_dir = root / 'pages'
    files_dir = root / 'files'
    meta_dir = root / 'meta'
    for d in (pages_dir, files_dir, meta_dir):
        d.mkdir(parents=True, exist_ok=True)

    (meta_dir / 'source_urls.txt').write_text('\n'.join(DEFAULT_SOURCES) + '\n', encoding='utf-8')

    page_manifest = []
    all_links: list[tuple[str, str, int]] = []

    # Depth 0 pages
    for i, src in enumerate(DEFAULT_SOURCES, start=1):
        txt, err = run_curl_text(src, timeout=args.page_timeout)
        page_file = pages_dir / safe_page_name(src, f'{i:02d}')
        rec = {
            'url': src,
            'depth': 0,
            'status': 'ok' if txt is not None else 'error',
            'error': err,
            'links': 0,
            'page_file': str(page_file),
        }
        if txt is not None:
            page_file.write_text(txt, encoding='utf-8')
            hrefs = extract_links(txt)
            rec['links'] = len(hrefs)
            for h in hrefs:
                u = urldefrag(urljoin(src, h))[0]
                all_links.append((src, u, 1))
        page_manifest.append(rec)

    # Depth 1 child pages
    child_candidates = []
    seen = set()
    for _, u, _ in all_links:
        sp = urlsplit(u)
        low = sp.path.lower()
        if sp.netloc not in ALLOWED_HOSTS:
            continue
        if not low.endswith('.html'):
            continue
        if not any(seg in low for seg in ['/samples/', '/reference/', '/guideline/', '/application/', '/topics/', '/info/']):
            continue
        if u in seen:
            continue
        seen.add(u)
        child_candidates.append(u)

    for i, u in enumerate(child_candidates[: args.max_child_pages], start=1):
        txt, err = run_curl_text(u, timeout=args.page_timeout)
        page_file = pages_dir / safe_page_name(u, f'c{i:03d}')
        rec = {
            'url': u,
            'depth': 1,
            'status': 'ok' if txt is not None else 'error',
            'error': err,
            'links': 0,
            'page_file': str(page_file),
        }
        if txt is not None:
            page_file.write_text(txt, encoding='utf-8')
            hrefs = extract_links(txt)
            rec['links'] = len(hrefs)
            for h in hrefs:
                absu = urldefrag(urljoin(u, h))[0]
                all_links.append((u, absu, 2))
        page_manifest.append(rec)

    # Attachment extraction
    att_rows = []
    seen_att = set()
    for frm, u, depth in all_links:
        path = urlsplit(u).path.lower()
        if path.endswith(ATT_EXTS) and u not in seen_att:
            seen_att.add(u)
            att_rows.append({'from': frm, 'url': u, 'depth': depth})

    # Download attachments incrementally
    file_manifest = []
    for row in att_rows:
        u = row['url']
        out = files_dir / safe_file_name(u)
        if out.exists() and out.stat().st_size > 0:
            ok, err = True, ''
            action = 'already_exists'
        else:
            ok, err = run_curl_file(u, out, timeout=args.file_timeout)
            action = 'downloaded' if ok else 'failed'

        file_manifest.append({
            'from': row['from'],
            'url': u,
            'file': str(out),
            'status': 'ok' if ok else 'error',
            'action': action,
            'error': None if ok else err,
            'bytes': out.stat().st_size if out.exists() else 0,
        })

    save_json(meta_dir / 'crawl_pages_manifest.json', page_manifest)
    save_json(meta_dir / 'attachment_urls.json', att_rows)
    save_json(meta_dir / 'download_manifest.json', file_manifest)
    build_indexes(meta_dir, file_manifest)

    pages_ok = sum(1 for x in page_manifest if x['status'] == 'ok')
    files_ok = sum(1 for x in file_manifest if x['status'] == 'ok')
    files_err = sum(1 for x in file_manifest if x['status'] != 'ok')
    summary = {
        'root': str(root),
        'pages_crawled': len(page_manifest),
        'pages_ok': pages_ok,
        'attachments_found': len(att_rows),
        'files_ok': files_ok,
        'files_error': files_err,
        'n2_index_csv': str(meta_dir / 'n2_index.csv'),
    }
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
