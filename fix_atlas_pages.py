#!/usr/bin/env python3
"""
fix_atlas_pages.py
Fixes two bugs in all atlas model-viewer pages:
  Bug #5: Blob URL memory leak — no URL.revokeObjectURL() call
  Bug #6: getImage() returns alien.png for blob:// URLs — fix to use data-model-name

Patches all 3 language versions: TR (atlas/), EN (eng/atlas/), RU (rus/atlas/)
"""

import os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Pattern 1: Fix blob URL leak in loadProtectedModel ───────────────────────
# Before:
#   const blob = await modelRes.blob();
#   viewer.src = URL.createObjectURL(blob);
# After:
#   const blob = await modelRes.blob();
#   if (viewer._blobUrl) URL.revokeObjectURL(viewer._blobUrl);
#   viewer._blobUrl = URL.createObjectURL(blob);
#   viewer.src = viewer._blobUrl;

BLOB_BEFORE = re.compile(
    r'(const blob = await modelRes\.blob\(\);)\s*\n(\s*)(viewer\.src = URL\.createObjectURL\(blob\);)',
    re.MULTILINE
)
BLOB_AFTER = (
    r'\1\n\2// Bug #5 fix: revoke previous blob URL to prevent memory leak\n'
    r'\2if (viewer._blobUrl) URL.revokeObjectURL(viewer._blobUrl);\n'
    r'\2viewer._blobUrl = URL.createObjectURL(blob);\n'
    r'\2viewer.src = viewer._blobUrl;'
)

# ── Pattern 2: Fix getImage() — use data-model-name attribute ─────────────────
# Before:
#   function getImage() {
#     var v = document.getElementById('mainViewer');
#     if (v) {
#       var src = v.getAttribute('src') || '';
#       var m = src.match(/\/assets\/models\/([^.]+)\.glb/);
#       if (m) return '/assets/models-pictures/' + m[1] + '.png';
#     }
#     return '/assets/icons/alien.png';
#   }
# After: check data-model-name first (blob-safe), fall back to src parse

OLD_GET_IMAGE = re.compile(
    r'function getImage\(\) \{\s*\n'
    r'\s*var v = document\.getElementById\(\'mainViewer\'\);\s*\n'
    r'\s*if \(v\) \{\s*\n'
    r'\s*var src = v\.getAttribute\(\'src\'\) \|\| \'\';\s*\n'
    r'\s*var m = src\.match\(\/\\\/assets\\\/models\\\/\(\[^.\]\+\)\\\.glb\/\);\s*\n'
    r'\s*if \(m\) return \'\/assets\/models-pictures\/\' \+ m\[1\] \+ \'\.png\';\s*\n'
    r'\s*\}\s*\n'
    r'\s*return \'\/assets\/icons\/alien\.png\';\s*\n'
    r'\s*\}',
    re.MULTILINE
)
NEW_GET_IMAGE = (
    "function getImage() {\n"
    "      var v = document.getElementById('mainViewer');\n"
    "      if (v) {\n"
    "        // Bug #6 fix: use data-model-name — always reliable even after src becomes blob://\n"
    "        var slug = v.dataset.modelName || v.getAttribute('data-model-name');\n"
    "        if (slug) return '/assets/models-pictures/' + slug + '.png';\n"
    "        // Fallback: parse src for backwards compat\n"
    "        var src = v.getAttribute('src') || '';\n"
    "        var m = src.match(/\\/assets\\/models\\/([^.]+)\\.glb/);\n"
    "        if (m) return '/assets/models-pictures/' + m[1] + '.png';\n"
    "      }\n"
    "      return '/assets/icons/alien.png';\n"
    "    }"
)

def patch_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        original = f.read()

    patched = original
    changed = []

    # Apply blob fix
    new, n = BLOB_BEFORE.subn(BLOB_AFTER, patched)
    if n:
        patched = new
        changed.append(f"blob-url-fix({n})")

    # Apply getImage fix
    new, n = OLD_GET_IMAGE.subn(NEW_GET_IMAGE, patched)
    if n:
        patched = new
        changed.append(f"getImage-fix({n})")

    if patched != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(patched)
        return changed
    return []

def main():
    atlas_dirs = [
        os.path.join(REPO, 'atlas'),
        os.path.join(REPO, 'eng', 'atlas'),
        os.path.join(REPO, 'rus', 'atlas'),
    ]

    total_files = 0
    patched_files = 0
    errors = []

    for base in atlas_dirs:
        if not os.path.isdir(base):
            print(f"  [SKIP] {base} — not found")
            continue
        for root, dirs, files in os.walk(base):
            for fname in files:
                if fname != 'index.html':
                    continue
                total_files += 1
                fpath = os.path.join(root, fname)
                try:
                    changes = patch_file(fpath)
                    if changes:
                        patched_files += 1
                        rel = os.path.relpath(fpath, REPO)
                        print(f"  ✅ {rel}: {', '.join(changes)}")
                except Exception as e:
                    errors.append((fpath, str(e)))
                    print(f"  ❌ {fpath}: {e}")

    print(f"\n── Summary ──────────────────────────")
    print(f"  Scanned : {total_files} files")
    print(f"  Patched : {patched_files} files")
    print(f"  Errors  : {len(errors)}")
    if errors:
        sys.exit(1)

if __name__ == '__main__':
    main()
