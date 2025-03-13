#!/usr/bin/env python
"""
Script to replace 'data/movie.csv' with '../notebooks/data/movie.csv' in all Jupyter notebooks
in the specified directory.
"""

import json
import os
import sys
from pathlib import Path

def fix_movie_paths(notebook_path):
    """Replace data/movie.csv with ../notebooks/data/movie.csv in a notebook."""
    print(f"Processing: {notebook_path}")
    
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    changes_made = 0
    
    # Process each cell
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            for i, line in enumerate(cell['source']):
                if 'data/movie.csv' in line:
                    cell['source'][i] = line.replace('data/movie.csv', '../notebooks/data/movie.csv')
                    changes_made += 1
    
    if changes_made > 0:
        print(f"  Made {changes_made} replacements")
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1)
    else:
        print("  No replacements needed")
    
    return changes_made

def main():
    """Main function to process all notebooks in a directory."""
    if len(sys.argv) < 2:
        print("Usage: python fix_movie_paths.py <directory>")
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
    
    total_changes = 0
    modified_notebooks = 0
    
    for notebook in notebooks:
        changes = fix_movie_paths(str(notebook))
        if changes > 0:
            modified_notebooks += 1
            total_changes += changes
    
    print(f"\nSummary: Modified {modified_notebooks} notebooks with {total_changes} total path replacements")

if __name__ == "__main__":
    main()
