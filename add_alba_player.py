#!/usr/bin/env python3
"""
Add Alba Audio Player to all model-viewer pages
"""

import os
import re
from pathlib import Path

# List of directories to scan for model-viewer pages
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
    '/workspaces/website-8.0/eng/atlas',
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

def process_html_file(filepath):
    """Process a single HTML file to add alba player if needed"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file already has alba player
    if 'id="albaPlayer"' in content:
        print(f"✓ Already has alba player: {filepath}")
        return False
    
    # Check if file has model-viewer
    if '<model-viewer' not in content:
        return False
    
    # Check if CSS link exists
    if 'alba-player.css' not in content:
        # Add CSS link after site.css
        content = content.replace(
            '<link rel="stylesheet" href="/assets/css/site.css" />',
            '<link rel="stylesheet" href="/assets/css/site.css" />\n  <link rel="stylesheet" href="/assets/css/alba-player.css" />'
        )
    
    # Check if JS link exists
    if 'alba-player.js' not in content:
        # Add JS link before closing body
        content = content.replace(
            '</body>',
            '  <script src="/assets/js/alba-player.js" defer></script>\n\n</body>'
        )
    
    # Find the closing </model-viewer> tag and add player after it
    # Pattern: </model-viewer> followed by optional whitespace and </div>
    pattern = r'(</model-viewer>\s*\n\s*</div>)'
    
    if not re.search(pattern, content):
        # Try alternative pattern - just </model-viewer> 
        pattern = r'(</model-viewer>)'
        match = re.search(pattern, content)
        if match:
            # Find the closing div
            end_pos = match.end()
            # Look for the next </div> after model-viewer
            remaining = content[end_pos:]
            div_match = re.search(r'\n\s*</div>', remaining)
            if div_match:
                insert_pos = end_pos + div_match.start()
                content = content[:insert_pos] + '\n\n' + ALBA_PLAYER_HTML + '\n  ' + content[insert_pos:]
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✓ Added alba player: {filepath}")
                return True
    else:
        match = re.search(pattern, content)
        if match:
            insert_pos = match.start(1)
            content = content[:insert_pos] + ALBA_PLAYER_HTML + '\n  ' + content[insert_pos:]
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Added alba player: {filepath}")
            return True
    
    return False

def main():
    processed = 0
    for dir_path in dirs_to_scan:
        index_file = os.path.join(dir_path, 'index.html')
        if os.path.exists(index_file):
            if process_html_file(index_file):
                processed += 1
        else:
            print(f"✗ Not found: {index_file}")
    
    print(f"\nTotal files updated: {processed}")

if __name__ == '__main__':
    main()
