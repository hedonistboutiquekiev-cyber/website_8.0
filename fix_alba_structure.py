#!/usr/bin/env python3
"""
Fix alba player placement - proper HTML structure
Alba player should be BEFORE model-viewer but INSIDE the container div
"""

import os
import re

dirs_to_scan = [
    '/workspaces/website-8.0/iss',
    '/workspaces/website-8.0/mars',
    '/workspaces/website-8.0/venus',
    '/workspaces/website-8.0/saturn',
    '/workspaces/website-8.0/hubble',
    '/workspaces/website-8.0/neptune',
    '/workspaces/website-8.0/uranus',
    '/workspaces/website-8.0/turksat-1A',
    '/workspaces/website-8.0/turksat-1B',
    '/workspaces/website-8.0/turksat-1C',
    '/workspaces/website-8.0/turksat-2A',
    '/workspaces/website-8.0/turksat-3A',
    '/workspaces/website-8.0/turksat-4A',
    '/workspaces/website-8.0/turksat-5A',
    '/workspaces/website-8.0/turksat-5B',
    '/workspaces/website-8.0/turksat-6A',
    '/workspaces/website-8.0/kepler',
    '/workspaces/website-8.0/exomars',
    '/workspaces/website-8.0/ingenuity',
    '/workspaces/website-8.0/perseverance',
    '/workspaces/website-8.0/opportunity',
    '/workspaces/website-8.0/spirit',
    '/workspaces/website-8.0/zhurong',
    '/workspaces/website-8.0/marsodyssey',
    '/workspaces/website-8.0/marsreconnaissance',
    '/workspaces/website-8.0/gokturk-1',
    '/workspaces/website-8.0/gokturk-2',
    '/workspaces/website-8.0/rasat',
    '/workspaces/website-8.0/imece',
    '/workspaces/website-8.0/voyager1',
    '/workspaces/website-8.0/eng/mars',
    '/workspaces/website-8.0/eng/gokturk-2',
    '/workspaces/website-8.0/eng/sputnik',
    '/workspaces/website-8.0/eng/turksat-2A',
    '/workspaces/website-8.0/eng/iss',
]

def get_page_id(filepath):
    """Extract page ID from filepath"""
    # /workspaces/website-8.0/mars/index.html -> mars
    # /workspaces/website-8.0/eng/mars/index.html -> mars
    parts = filepath.replace('\\', '/').split('/')
    if 'eng' in parts:
        # eng/mars/index.html -> mars
        idx = parts.index('eng')
        return parts[idx + 1]
    else:
        # mars/index.html -> mars
        return parts[-2]

def fix_alba_structure(filepath):
    """Fix alba player HTML structure"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    page_id = get_page_id(filepath)
    
    # First, remove all alba player blocks
    # Pattern: <!-- Alba Futuristic Audio Player --> ... </div>
    alba_pattern = r'\n\s*<!-- Alba Futuristic Audio Player -->.*?</div>\s*(?=\n\s*(?:<model-viewer|</div>))'
    
    content = re.sub(alba_pattern, '', content, flags=re.DOTALL)
    
    # Now find the <p> tag inside container and add alba player after it
    # Pattern: </p> before <model-viewer (or other content)
    p_pattern = r'(</p>)\s*\n\s*(?=<model-viewer|<!--)'
    
    alba_html = f'''

    <!-- Alba Futuristic Audio Player -->
    <div id="albaPlayer">
      <div class="alba-track-name">
        <span class="alba-track-dot"></span>
        <span id="albaTrackLabel">{page_id.upper()} — Sesli Anlatım</span>
      </div>
      <div class="alba-player-row">
        <button class="alba-btn" id="albaPlayPause" title="Oynat / Duraklat" aria-label="Oynat">
          <svg id="albaIconPlay" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
          <svg id="albaIconPause" viewBox="0 0 24 24" fill="currentColor" style="display:none"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
        </button>
        <button class="alba-btn alba-btn-stop" id="albaStop" title="Durdur" aria-label="Durdur">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 6h12v12H6z"/></svg>
        </button>
        <div class="alba-progress-wrap" id="albaProgressWrap">
          <div class="alba-loading-bars" id="albaLoadingBars">
            <span></span><span></span><span></span><span></span><span></span>
            <span></span><span></span><span></span><span></span><span></span>
          </div>
          <div class="alba-progress-track" id="albaProgressTrack">
            <div class="alba-progress-fill" id="albaProgressFill"></div>
            <div class="alba-progress-thumb" id="albaProgressThumb"></div>
          </div>
          <div class="alba-eq" id="albaEq">
            <span></span><span></span><span></span><span></span><span></span>
          </div>
        </div>
        <div class="alba-time">
          <span id="albaCurrent">0:00</span>
          <span class="alba-time-sep">/</span>
          <span id="albaDuration">—:——</span>
        </div>
      </div>
      <div class="alba-status" id="albaStatus">Müzik seç ve dinle 🎵</div>
    </div>'''
    
    # Replace pattern
    match = re.search(p_pattern, content)
    if match:
        content = content[:match.end(1)] + alba_html + content[match.end(1):]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Fixed structure: {filepath}")
        return True
    
    return False

def main():
    fixed = 0
    for dir_path in dirs_to_scan:
        index_file = os.path.join(dir_path, 'index.html')
        if os.path.exists(index_file):
            if fix_alba_structure(index_file):
                fixed += 1
        else:
            print(f"✗ Not found: {index_file}")
    
    print(f"\nTotal files fixed: {fixed}")

if __name__ == '__main__':
    main()
