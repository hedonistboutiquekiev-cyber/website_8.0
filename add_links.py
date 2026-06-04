#!/usr/bin/env python3
"""
Add CSS and JS links to all model-viewer pages if missing
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

def add_missing_links(filepath):
    """Add missing CSS and JS links"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    updated = False
    
    # Check and add CSS link if missing
    if 'alba-player.css' not in content:
        # Find site.css link
        match = re.search(r'<link rel="stylesheet" href="/assets/css/site\.css" />', content)
        if match:
            # Add alba-player.css after site.css
            site_css_end = match.end()
            content = content[:site_css_end] + '\n  <link rel="stylesheet" href="/assets/css/alba-player.css" />' + content[site_css_end:]
            updated = True
    
    # Check and add JS link if missing
    if 'alba-player.js' not in content:
        # Find </body> tag
        match = re.search(r'</body>', content)
        if match:
            # Add alba-player.js before </body>
            body_end = match.start()
            content = content[:body_end] + '  <script src="/assets/js/alba-player.js" defer></script>\n\n' + content[body_end:]
            updated = True
    
    if updated:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Added links: {filepath}")
        return True
    else:
        print(f"✓ Already has links: {filepath}")
        return False

def main():
    updated = 0
    for dir_path in dirs_to_scan:
        index_file = os.path.join(dir_path, 'index.html')
        if os.path.exists(index_file):
            if add_missing_links(index_file):
                updated += 1
        else:
            print(f"✗ Not found: {index_file}")
    
    print(f"\nTotal files updated: {updated}")

if __name__ == '__main__':
    main()
