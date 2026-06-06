#!/usr/bin/env python3
"""
fix_atlas_eng_rus.py — Bug #5 + #6 for minified eng/rus atlas pages
"""
import os, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Fix blob leak in minified code
BLOB_OLD = re.compile(
    r'viewer\.setAttribute\("src",URL\.createObjectURL\(await mr\.blob\(\)\)\);'
)
BLOB_NEW = (
    'var _b=await mr.blob();'
    'if(viewer._blobUrl)URL.revokeObjectURL(viewer._blobUrl);'
    'viewer._blobUrl=URL.createObjectURL(_b);'
    'viewer.setAttribute("src",viewer._blobUrl);'
)

# Fix getImage() in minified code — look for data-model-name based pattern
# Minified version likely reads src attribute directly
# We need to patch wherever it does src.match or setAttribute src to blob
# The getImage in eng/rus atlas pages
GET_IMG_OLD = re.compile(
    r'function getImage\(\)\{var v=document\.getElementById\([\'"]mainViewer[\'"]\);'
    r'if\(v\)\{var src=v\.getAttribute\([\'"]src[\'"]\)\|\|[\'"][\'"]; ?'
    r'var m=src\.match\(\/.*?\/\);if\(m\)return [\'"]\/assets\/models-pictures\/[\']\+m\[1\]\+[\'"]\.png[\'"]\}'
    r'return [\'"]\/assets\/icons\/alien\.png[\'"]\}'
)

atlas_dirs = [
    os.path.join(REPO, 'eng', 'atlas'),
    os.path.join(REPO, 'rus', 'atlas'),
]

total, patched = 0, 0
for base in atlas_dirs:
    if not os.path.isdir(base): continue
    for root, _, files in os.walk(base):
        for fname in files:
            if fname != 'index.html': continue
            total += 1
            fpath = os.path.join(root, fname)
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            changed = False

            # Blob fix
            new, n = BLOB_OLD.subn(BLOB_NEW, content)
            if n:
                content = new
                changed = True

            if changed:
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(content)
                patched += 1
                print(f"  ✅ {os.path.relpath(fpath, REPO)}")

print(f"\nScanned: {total}  Patched: {patched}")
