#!/usr/bin/env python
"""
Script to fix common issues in Jupyter notebooks.
"""

import json
import os
import re
import sys
from pathlib import Path
import shutil

def fix_notebook(notebook_path):
    """Fix common issues in a notebook and save the changes."""
    print(f"\nFixing notebook: {notebook_path}")
    
    # Create a backup of the original file
    backup_path = f"{notebook_path}.bak"
    shutil.copy2(notebook_path, backup_path)
    print(f"Created backup at: {backup_path}")
    
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    fixes_made = 0
    
    # Fix cells with code
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            original_source = source
            
            # Fix deprecated pandas methods
            if 'get_dtype_counts()' in source:
                source = source.replace('get_dtype_counts()', 'dtypes.value_counts()')
                fixes_made += 1
                print(f"  Fixed: Replaced 'get_dtype_counts()' with 'dtypes.value_counts()' in cell {i}")
            
            # Fix list subtraction
            list_subtraction = re.search(r'\[[^\]]*\]\s*-\s*\d+', source)
            if list_subtraction:
                match = list_subtraction.group(0)
                list_part = re.search(r'\[[^\]]*\]', match).group(0)
                num_part = re.search(r'\d+', match.split('-')[1]).group(0)
                replacement = f'np.array({list_part}) - {num_part}'
                source = source.replace(match, replacement)
                fixes_made += 1
                print(f"  Fixed: Replaced '{match}' with '{replacement}' in cell {i}")
            
            # Fix pd.set_option with multiple options
            set_option_match = re.search(r"pd\.set_option\(['\"]([^'\"]+)['\"],\s*([^,]+),\s*['\"]([^'\"]+)['\"],\s*([^)]+)\)", source)
            if set_option_match:
                opt1 = set_option_match.group(1)
                val1 = set_option_match.group(2)
                opt2 = set_option_match.group(3)
                val2 = set_option_match.group(4)
                
                # Add display. prefix if missing
                if not opt1.startswith('display.'):
                    opt1 = f'display.{opt1}'
                if not opt2.startswith('display.'):
                    opt2 = f'display.{opt2}'
                
                replacement = f"pd.set_option('{opt1}', {val1})\npd.set_option('{opt2}', {val2})"
                source = source.replace(set_option_match.group(0), replacement)
                fixes_made += 1
                print(f"  Fixed: Split multiple pd.set_option calls in cell {i}")
            
            # Fix missing display. prefix in pd.set_option
            set_option_single = re.search(r"pd\.set_option\(['\"](?!display\.)([^'\"]+)['\"]", source)
            if set_option_single and not set_option_match:
                opt = set_option_single.group(1)
                source = source.replace(f"'{opt}'", f"'display.{opt}'")
                fixes_made += 1
                print(f"  Fixed: Added 'display.' prefix to '{opt}' in cell {i}")
            
            # Update the cell source if changes were made
            if source != original_source:
                notebook['cells'][i]['source'] = [source]
    
    if fixes_made > 0:
        # Save the updated notebook
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1)
        print(f"Made {fixes_made} fixes to {notebook_path}")
    else:
        print(f"No issues to fix in {notebook_path}")
        # Remove the backup if no changes were made
        os.remove(backup_path)
        print(f"Removed unnecessary backup: {backup_path}")
    
    return fixes_made

def main():
    """Main function to fix all notebooks in a directory."""
    if len(sys.argv) < 2:
        print("Usage: python fix_notebooks.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a directory")
        sys.exit(1)
    
    notebooks = list(Path(directory).glob('*.ipynb'))
    
    if not notebooks:
        print(f"No notebooks found in {directory}")
        sys.exit(0)
    
    print(f"Found {len(notebooks)} notebooks in {directory}")
    
    total_fixes = 0
    fixed_notebooks = 0
    
    for notebook in notebooks:
        fixes = fix_notebook(str(notebook))
        total_fixes += fixes
        if fixes > 0:
            fixed_notebooks += 1
    
    print(f"\nSummary: Fixed {total_fixes} issues in {fixed_notebooks} notebooks")
    print("Notebooks that were fixed have backups with the .bak extension")

if __name__ == "__main__":
    main()
