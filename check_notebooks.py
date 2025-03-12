#!/usr/bin/env python
"""
Script to check Jupyter notebooks for common errors and provide fixes.
"""

import json
import os
import re
import sys
from pathlib import Path

def check_notebook(notebook_path):
    """Check a notebook for common issues and suggest fixes."""
    print(f"\nChecking notebook: {notebook_path}")
    
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    issues = []
    
    # Check for cells with code
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            
            # Check for deprecated pandas methods
            if 'get_dtype_counts()' in source:
                issues.append({
                    'cell_index': i,
                    'issue': 'Deprecated method: get_dtype_counts()',
                    'fix': 'Replace with: dtypes.value_counts()',
                    'code': source,
                    'fixed_code': source.replace('get_dtype_counts()', 'dtypes.value_counts()')
                })
            
            # Check for list subtraction
            list_subtraction = re.search(r'\[[^\]]*\]\s*-\s*\d+', source)
            if list_subtraction:
                match = list_subtraction.group(0)
                list_part = re.search(r'\[[^\]]*\]', match).group(0)
                num_part = re.search(r'\d+', match.split('-')[1]).group(0)
                issues.append({
                    'cell_index': i,
                    'issue': f'Unsupported operation: {match}',
                    'fix': f'Replace with: [x - {num_part} for x in {list_part}] or np.array({list_part}) - {num_part}',
                    'code': source,
                    'fixed_code': source.replace(match, f'[x - {num_part} for x in {list_part}]')
                })
            
            # Check for pd.set_option with multiple options
            set_option_match = re.search(r"pd\.set_option\(['\"]([^'\"]+)['\"],\s*[^,]+,\s*['\"]([^'\"]+)['\"]", source)
            if set_option_match:
                opt1 = set_option_match.group(1)
                opt2 = re.search(r"pd\.set_option\([^,]+,\s*[^,]+,\s*['\"]([^'\"]+)['\"]", source).group(1)
                val1 = re.search(r"pd\.set_option\([^,]+,\s*([^,]+),", source).group(1)
                val2 = re.search(r"pd\.set_option\([^,]+,\s*[^,]+,\s*[^,]+,\s*([^)]+)", source).group(1)
                
                # Check if display. prefix is missing
                if not opt1.startswith('display.'):
                    opt1 = f'display.{opt1}'
                if not opt2.startswith('display.'):
                    opt2 = f'display.{opt2}'
                
                fix = f"pd.set_option('{opt1}', {val1})\npd.set_option('{opt2}', {val2})"
                issues.append({
                    'cell_index': i,
                    'issue': 'Multiple options in pd.set_option()',
                    'fix': 'Split into separate calls',
                    'code': source,
                    'fixed_code': source.replace(set_option_match.group(0), fix)
                })
            
            # Check for missing display. prefix in pd.set_option
            set_option_single = re.search(r"pd\.set_option\(['\"](?!display\.)([^'\"]+)['\"]", source)
            if set_option_single and not set_option_match:
                opt = set_option_single.group(1)
                fixed = source.replace(f"'{opt}'", f"'display.{opt}'")
                issues.append({
                    'cell_index': i,
                    'issue': f"Missing 'display.' prefix in option: {opt}",
                    'fix': f"Add 'display.' prefix: 'display.{opt}'",
                    'code': source,
                    'fixed_code': fixed
                })
    
    return issues

def main():
    """Main function to check all notebooks in a directory."""
    if len(sys.argv) < 2:
        print("Usage: python check_notebooks.py <directory>")
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
    
    all_issues = {}
    
    for notebook in notebooks:
        issues = check_notebook(str(notebook))
        if issues:
            all_issues[str(notebook)] = issues
    
    if all_issues:
        print("\n\n===== SUMMARY OF ISSUES =====")
        for notebook, issues in all_issues.items():
            print(f"\n{notebook}: {len(issues)} issues found")
            for i, issue in enumerate(issues):
                print(f"  {i+1}. Cell {issue['cell_index']}: {issue['issue']}")
                print(f"     Fix: {issue['fix']}")
                print(f"     Original code: {issue['code'].strip()}")
                print(f"     Fixed code: {issue['fixed_code'].strip()}")
    else:
        print("\nNo issues found in any notebooks!")

if __name__ == "__main__":
    main()
