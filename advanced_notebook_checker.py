#!/usr/bin/env python
"""
Advanced script to check Jupyter notebooks for common issues with pandas and file paths.
"""

import json
import os
import re
import sys
from pathlib import Path
import pandas as pd

def check_notebook_for_issues(notebook_path):
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
            deprecated_methods = [
                ('get_dtype_counts()', 'dtypes.value_counts()'),
                ('append(', 'concat([df1, df2], ignore_index=True)'),
                ('ix[', 'loc[ or iloc['),
                ('as_matrix()', 'to_numpy()'),
                ('read_table(', 'read_csv('),
                ('convert_objects(', 'astype()'),
                ('pd.TimeGrouper(', 'pd.Grouper(freq='),
                ('pd.SparseDataFrame(', 'pd.DataFrame(...).sparse.from_spmatrix('),
                ('pd.SparseSeries(', 'pd.Series(..., dtype="Sparse")'),
                ('pd.Panel(', 'Use MultiIndex DataFrame instead'),
                ('pd.scatter_matrix(', 'pd.plotting.scatter_matrix('),
                ('pd.tools.plotting.', 'pd.plotting.'),
                ('pd.tseries.plotting.', 'pd.plotting.'),
                ('pd.stats.', 'Use statsmodels instead'),
                ('pd.rolling_', 'df.rolling().'),
                ('pd.expanding_', 'df.expanding().'),
                ('pd.ewma(', 'df.ewm().mean()'),
                ('pd.ewmstd(', 'df.ewm().std()'),
                ('pd.ewmvar(', 'df.ewm().var()'),
                ('pd.ewmcorr(', 'df.ewm().corr()'),
                ('pd.ewmcov(', 'df.ewm().cov()'),
                ('isnull()', 'isna()'),
                ('notnull()', 'notna()'),
                ('pd.TimeGrouper(', 'pd.Grouper(freq='),
                ('sort(', 'sort_values('),
                ('sort_index(inplace=True)', 'sort_index()'),
                ('sort_values(inplace=True)', 'sort_values()'),
                ('reset_index(inplace=True)', 'reset_index()'),
                ('set_index(inplace=True)', 'set_index()'),
                ('fillna(inplace=True)', 'fillna()'),
                ('dropna(inplace=True)', 'dropna()'),
                ('drop(inplace=True)', 'drop()'),
                ('rename(inplace=True)', 'rename()'),
                ('replace(inplace=True)', 'replace()'),
            ]
            
            for old, new in deprecated_methods:
                if old in source:
                    issues.append({
                        'cell_index': i,
                        'issue': f'Deprecated method: {old}',
                        'fix': f'Replace with: {new}',
                        'code': source,
                        'severity': 'high'
                    })
            
            # Check for file path issues
            file_path_patterns = [
                r"pd\.read_csv\(['\"]([^'\"]+)['\"]",
                r"pd\.read_excel\(['\"]([^'\"]+)['\"]",
                r"pd\.read_parquet\(['\"]([^'\"]+)['\"]",
                r"pd\.read_hdf\(['\"]([^'\"]+)['\"]",
                r"pd\.read_pickle\(['\"]([^'\"]+)['\"]",
                r"pd\.read_json\(['\"]([^'\"]+)['\"]",
                r"pd\.read_html\(['\"]([^'\"]+)['\"]",
                r"pd\.read_sas\(['\"]([^'\"]+)['\"]",
                r"pd\.read_stata\(['\"]([^'\"]+)['\"]",
                r"pd\.read_feather\(['\"]([^'\"]+)['\"]",
                r"pd\.read_spss\(['\"]([^'\"]+)['\"]",
                r"pd\.read_orc\(['\"]([^'\"]+)['\"]",
                r"pd\.read_sql\(['\"]([^'\"]+)['\"]",
                r"open\(['\"]([^'\"]+)['\"]",
                r"with open\(['\"]([^'\"]+)['\"]",
                r"os\.path\.join\(['\"]([^'\"]+)['\"]",
                r"Path\(['\"]([^'\"]+)['\"]",
            ]
            
            for pattern in file_path_patterns:
                matches = re.finditer(pattern, source)
                for match in matches:
                    file_path = match.group(1)
                    # Skip URLs and variable references
                    if file_path.startswith(('http://', 'https://', 'ftp://', '{', '$')):
                        continue
                    
                    # Skip paths that are clearly variables
                    if not any(char in file_path for char in ['/', '\\', '.']):
                        continue
                    
                    # Check if the file path exists relative to the notebook
                    notebook_dir = os.path.dirname(notebook_path)
                    full_path = os.path.join(notebook_dir, file_path)
                    if not os.path.exists(full_path) and not file_path.startswith('/'):
                        issues.append({
                            'cell_index': i,
                            'issue': f'File path may not exist: {file_path}',
                            'fix': 'Update path or create the file',
                            'code': source,
                            'severity': 'medium'
                        })
            
            # Check for pandas set_option issues
            set_option_match = re.search(r"pd\.set_option\(['\"]([^'\"]+)['\"]", source)
            if set_option_match:
                option = set_option_match.group(1)
                if not option.startswith('display.'):
                    issues.append({
                        'cell_index': i,
                        'issue': f"Missing 'display.' prefix in option: {option}",
                        'fix': f"Add 'display.' prefix: 'display.{option}'",
                        'code': source,
                        'severity': 'medium'
                    })
            
            # Check for multiple options in pd.set_option
            set_option_multiple = re.search(r"pd\.set_option\([^,]+,[^,]+,[^,]+", source)
            if set_option_multiple:
                issues.append({
                    'cell_index': i,
                    'issue': 'Multiple options in pd.set_option()',
                    'fix': 'Split into separate calls',
                    'code': source,
                    'severity': 'high'
                })
            
            # Check for unsupported operations
            list_subtraction = re.search(r'\[[^\]]*\]\s*-\s*\d+', source)
            if list_subtraction:
                match = list_subtraction.group(0)
                issues.append({
                    'cell_index': i,
                    'issue': f'Unsupported operation: {match}',
                    'fix': 'Use list comprehension or numpy array',
                    'code': source,
                    'severity': 'high'
                })
            
            # Check for pandas version-specific code
            if 'pd.__version__' in source or 'pandas.__version__' in source:
                issues.append({
                    'cell_index': i,
                    'issue': 'Version-specific code detected',
                    'fix': f'Current pandas version: {pd.__version__}. May need updates.',
                    'code': source,
                    'severity': 'low'
                })
    
    return issues

def main():
    """Main function to check all notebooks in a directory."""
    if len(sys.argv) < 2:
        print("Usage: python advanced_notebook_checker.py <directory>")
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
    print(f"Current pandas version: {pd.__version__}")
    
    all_issues = {}
    total_high_severity = 0
    total_medium_severity = 0
    total_low_severity = 0
    
    for notebook in notebooks:
        issues = check_notebook_for_issues(str(notebook))
        if issues:
            all_issues[str(notebook)] = issues
            high_severity = sum(1 for issue in issues if issue['severity'] == 'high')
            medium_severity = sum(1 for issue in issues if issue['severity'] == 'medium')
            low_severity = sum(1 for issue in issues if issue['severity'] == 'low')
            total_high_severity += high_severity
            total_medium_severity += medium_severity
            total_low_severity += low_severity
    
    if all_issues:
        print("\n\n===== SUMMARY OF ISSUES =====")
        print(f"Total issues: {total_high_severity + total_medium_severity + total_low_severity}")
        print(f"High severity issues: {total_high_severity}")
        print(f"Medium severity issues: {total_medium_severity}")
        print(f"Low severity issues: {total_low_severity}")
        
        for notebook, issues in all_issues.items():
            print(f"\n{notebook}: {len(issues)} issues found")
            high_severity = [issue for issue in issues if issue['severity'] == 'high']
            medium_severity = [issue for issue in issues if issue['severity'] == 'medium']
            low_severity = [issue for issue in issues if issue['severity'] == 'low']
            
            if high_severity:
                print("  HIGH SEVERITY ISSUES:")
                for i, issue in enumerate(high_severity):
                    print(f"    {i+1}. Cell {issue['cell_index']}: {issue['issue']}")
                    print(f"       Fix: {issue['fix']}")
            
            if medium_severity:
                print("  MEDIUM SEVERITY ISSUES:")
                for i, issue in enumerate(medium_severity):
                    print(f"    {i+1}. Cell {issue['cell_index']}: {issue['issue']}")
                    print(f"       Fix: {issue['fix']}")
            
            if low_severity:
                print("  LOW SEVERITY ISSUES:")
                for i, issue in enumerate(low_severity):
                    print(f"    {i+1}. Cell {issue['cell_index']}: {issue['issue']}")
                    print(f"       Fix: {issue['fix']}")
    else:
        print("\nNo issues found in any notebooks!")

if __name__ == "__main__":
    main()
