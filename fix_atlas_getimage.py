#!/usr/bin/env python3
"""
fix_atlas_getimage.py — fixes Bug #6: getImage() returns alien.png for blob:// URLs
"""
import os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OLD = """    function getImage() {
      var v = document.getElementById('mainViewer');
      if (v) {
        var src = v.getAttribute('src') || '';
        var m = src.match(/\\/assets\\/models\\/([^.]+)\\.glb/);
        if (m) return '/assets/models-pictures/' + m[1] + '.png';
      }
      return '/assets/icons/alien.png';
    }"""

NEW = """    function getImage() {
      var v = document.getElementById('mainViewer');
      if (v) {
        // Bug #6 fix: data-model-name is always set, not affected by blob:// src
        var slug = v.dataset.modelName || v.getAttribute('data-model-name');
        if (slug) return '/assets/models-pictures/' + slug + '.png';
        // Fallback: parse src (works before model loads as blob)
        var src = v.getAttribute('src') || '';
        var m = src.match(/\\/assets\\/models\\/([^.]+)\\.glb/);
        if (m) return '/assets/models-pictures/' + m[1] + '.png';
      }
      return '/assets/icons/alien.png';
    }"""

def patch(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if OLD not in content:
        return False
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.replace(OLD, NEW, 1))
    return True

atlas_dirs = [
    os.path.join(REPO, 'atlas'),
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
            if patch(fpath):
                patched += 1
                print(f"  ✅ {os.path.relpath(fpath, REPO)}")

print(f"\nScanned: {total}  Patched: {patched}")
