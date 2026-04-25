#!/usr/bin/env python3
"""
Update reports/manifest.json with the latest audit result.
Reads reports/_latest_meta.json (written by run_audit.py) and
prepends the entry to the manifest, keeping the 200 most recent reports.
"""

import json, os, sys

REPORTS_DIR   = os.path.join(os.path.dirname(__file__), '..', 'reports')
META_FILE     = os.path.join(REPORTS_DIR, '_latest_meta.json')
MANIFEST_FILE = os.path.join(REPORTS_DIR, 'manifest.json')
MAX_REPORTS   = 200

def main():
    if not os.path.isfile(META_FILE):
        print('No _latest_meta.json found — nothing to update.', file=sys.stderr)
        sys.exit(0)

    with open(META_FILE) as f:
        meta = json.load(f)

    # Load or init manifest
    if os.path.isfile(MANIFEST_FILE):
        with open(MANIFEST_FILE) as f:
            manifest = json.load(f)
    else:
        manifest = {'reports': []}

    if 'reports' not in manifest:
        manifest['reports'] = []

    # Remove any existing entry for same filename (idempotent)
    manifest['reports'] = [r for r in manifest['reports'] if r.get('filename') != meta.get('filename')]

    # Prepend latest
    manifest['reports'].insert(0, meta)

    # Trim to max
    manifest['reports'] = manifest['reports'][:MAX_REPORTS]

    with open(MANIFEST_FILE, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"Manifest updated: {len(manifest['reports'])} report(s) · latest: {meta['domain']} {meta['grade']} {meta['total_score']}/30")

if __name__ == '__main__':
    main()
