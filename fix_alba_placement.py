#!/usr/bin/env python3
"""
Fix Alba Audio Player placement - move from inside model-viewer to after it
"""

import os
import re
from pathlib import Path

# List of directories to scan for model-viewer pages
dirs_to_scan = [
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

ALBA_PLAYER_HTML = '''    <!-- Alba Futuristic Audio Player -->
    <div id="albaPlayer">
      <div class="alba-track-name">
        <span class="alba-track-dot"></span>
        <span id="albaTrackLabel">Uzay Modeli</span>
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

def fix_alba_placement(filepath):
    """Move alba player from inside model-viewer to after it"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to find alba player inside model-viewer
    pattern = r'(</model-viewer>)\s*\n\s*(<!-- Alba Futuristic Audio Player -->.*?</div>\n\s*</div>)'
    
    match = re.search(pattern, content, re.DOTALL)
    if match:
        # Extract the alba player
        alba_start = content.find('<!-- Alba Futuristic Audio Player -->', match.start(1))
        alba_end = content.find('</div>', alba_start)
        # Find the closing div
        alba_end = content.find('</div>', alba_end) + 6
        
        alba_html = content[alba_start:alba_end]
        
        # Remove it from inside model-viewer
        content = content[:alba_start] + content[alba_end:]
        
        # Find </model-viewer> tag
        model_viewer_end = content.find('</model-viewer>')
        if model_viewer_end != -1:
            model_viewer_end += len('</model-viewer>')
            # Insert alba player after </model-viewer>
            content = content[:model_viewer_end] + '\n\n' + alba_html + '\n' + content[model_viewer_end:]
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Fixed alba placement: {filepath}")
            return True
    
    return False

def main():
    fixed = 0
    for dir_path in dirs_to_scan:
        index_file = os.path.join(dir_path, 'index.html')
        if os.path.exists(index_file):
            if fix_alba_placement(index_file):
                fixed += 1
        else:
            print(f"✗ Not found: {index_file}")
    
    print(f"\nTotal files fixed: {fixed}")

if __name__ == '__main__':
    main()
