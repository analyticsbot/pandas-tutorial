#!/usr/bin/env python3
"""
Script to standardize Jupyter notebooks formatting.
This script will export the notebooks to Python files, modify them, and then convert them back.
"""

import os
import json
import sys
import subprocess

# Notebooks to standardize
notebooks = os.listdir("notebooks/")

# Base directory
base_dir = "/Users/neo/Downloads/Personal/Projects/pandas-tutorial/notebooks"

def standardize_notebook(notebook_path):
    """Standardize a single notebook's formatting."""
    print(f"Standardizing {notebook_path}...")
    
    # Read the notebook file
    with open(notebook_path, 'r') as f:
        notebook_content = json.load(f)
    
    # Process each cell
    for cell in notebook_content['cells']:
        if cell['cell_type'] == 'markdown':
            source = cell['source']
            
            # Replace heading formats
            if source and source[0].startswith('# '):
                # Convert main heading to #### format
                source[0] = source[0].replace('# ', '#### ')
            
            # Replace section headings
            for i, line in enumerate(source):
                if line.startswith('## '):
                    source[i] = line.replace('## ', '##### ')
            
            # Update the cell source
            cell['source'] = source
    
    # Write the updated notebook back
    with open(notebook_path, 'w') as f:
        json.dump(notebook_content, f, indent=1)
    
    print(f"Standardized {notebook_path}")

def main():
    """Main function to standardize all notebooks."""
    for notebook in notebooks:
        notebook_path = os.path.join(base_dir, notebook)
        if os.path.exists(notebook_path):
            standardize_notebook(notebook_path)
        else:
            print(f"Warning: {notebook_path} not found")

if __name__ == "__main__":
    main()
