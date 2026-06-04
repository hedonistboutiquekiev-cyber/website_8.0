#!/usr/bin/env python3
"""
Добавляет недостающие <model-viewer> элементы в файлы index.html.
Ищет files где есть <div class="alba-status"> но нет <model-viewer>.
"""

import re
from pathlib import Path

def get_model_name(filepath):
    """Извлекает имя модели из пути файла"""
    parent_folder = filepath.parent.name
    # Преобразуем имя папки в kebab-case для имена модели
    return parent_folder.lower()

def fix_file(filepath):
    """Добавляет <model-viewer> если его нет"""
    content = filepath.read_text(encoding='utf-8')
    
    # Пропускаем если уже есть model-viewer
    if '<model-viewer' in content:
        return False
    
    # Пропускаем если нет alba-status (значит это не страница модели)
    if 'alba-status' not in content:
        return False
    
    model_name = get_model_name(filepath)
    
    # Ищем паттерн: </p> ... <div class="alba-status"
    # и вставляем <model-viewer> между ними
    pattern = r'(</p>)\s*\n(\s*)<div class="alba-status"'
    replacement = rf'\1\n\2<model-viewer src="/assets/models/{model_name}.glb" data-model-name="{model_name}" camera-controls ar ar-modes="webxr scene-viewer quick-look" auto-rotate></model-viewer>\n\n\2<div class="alba-status"'
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        filepath.write_text(new_content, encoding='utf-8')
        return True
    
    return False

def main():
    root = Path('/workspaces/website_8.0')
    
    # Исключаем эти папки
    exclude_dirs = {'atlas', 'eng', 'rus', 'assets', 'node_modules', '.git'}
    
    fixed = []
    skipped = []
    
    for filepath in sorted(root.rglob('index.html')):
        # Пропускаем исключённые папки
        if any(part in exclude_dirs for part in filepath.parts):
            continue
        
        # Пропускаем если это не прямая подпапка или гнезда не более 2 уровней
        if len(filepath.relative_to(root).parts) > 2:
            continue
        
        try:
            if fix_file(filepath):
                fixed.append(str(filepath.relative_to(root)))
                print(f"✓ Fixed: {filepath.relative_to(root)}")
            else:
                skipped.append(str(filepath.relative_to(root)))
        except Exception as e:
            print(f"✗ Error in {filepath.relative_to(root)}: {e}")
    
    print(f"\n=== Summary ===")
    print(f"Fixed: {len(fixed)}")
    print(f"Skipped/Already OK: {len(skipped)}")

if __name__ == '__main__':
    main()
