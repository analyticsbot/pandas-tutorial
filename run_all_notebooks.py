#!/usr/bin/env python3
"""
Script to check all notebooks for syntax errors without executing them.
This is a safer approach than trying to execute all cells, as it will only check
for syntax errors and not try to run potentially problematic code.
"""

import os
import sys
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
import argparse

def check_notebook_syntax(notebook_path):
    """
    Check notebook for syntax errors without executing it.
    
    Args:
        notebook_path (str): Path to the notebook file
        
    Returns:
        tuple: (notebook_path, success, error_message)
    """
    try:
        print(f"Checking {os.path.basename(notebook_path)}...")
        
        # Load the notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        # Check each code cell for syntax errors
        syntax_errors = []
        for i, cell in enumerate(nb.cells):
            if cell.cell_type == 'code':
                # Skip empty cells
                if not cell.source.strip():
                    continue
                    
                try:
                    # Try to compile the code to check for syntax errors
                    # Some cells might have IPython magic commands or other non-standard Python
                    # that won't compile with the standard Python compiler
                    # We'll do our best to handle these cases
                    
                    # Remove IPython magic commands (lines starting with %)
                    code_lines = []
                    for line in cell.source.split('\n'):
                        if not line.strip().startswith('%'):
                            code_lines.append(line)
                    
                    # Skip if the cell only contained magic commands
                    if not ''.join(code_lines).strip():
                        continue
                        
                    # Try to compile the code
                    compile('\n'.join(code_lines), f"<Cell {i}>", 'exec')
                except SyntaxError as e:
                    syntax_errors.append(f"Cell {i}: {str(e)}")
                except Exception as e:
                    # Catch other compilation errors
                    syntax_errors.append(f"Cell {i}: {type(e).__name__}: {str(e)}")
        
        if syntax_errors:
            return (notebook_path, False, "\n".join(syntax_errors))
        else:
            return (notebook_path, True, "No syntax errors found")
    
    except Exception as e:
        return (notebook_path, False, str(e))

def main():
    parser = argparse.ArgumentParser(description='Check all Jupyter notebooks for syntax errors')
    parser.add_argument('--notebooks-dir', type=str, default='notebooks', 
                        help='Directory containing the notebooks')
    parser.add_argument('--max-workers', type=int, default=4, 
                        help='Maximum number of parallel workers')
    parser.add_argument('--pattern', type=str, default='part_*.ipynb',
                        help='Pattern to match notebook files')
    parser.add_argument('--limit', type=int, default=None,
                        help='Limit the number of notebooks to process')
    
    args = parser.parse_args()
    
    # Get all notebook files
    import glob
    notebook_dir = args.notebooks_dir
    notebook_pattern = os.path.join(notebook_dir, args.pattern)
    notebook_files = glob.glob(notebook_pattern)
    
    # Filter out any notebooks with "_executed" in the name
    notebook_files = [nb for nb in notebook_files if '_executed' not in nb]
    
    # Limit the number of notebooks if requested
    if args.limit is not None and args.limit > 0:
        notebook_files = notebook_files[:args.limit]
    
    if not notebook_files:
        print(f"No notebooks found matching pattern: {notebook_pattern}")
        return
    
    print(f"Found {len(notebook_files)} notebooks to check")
    
    # Check notebooks in parallel
    successful = []
    failed = []
    
    with ProcessPoolExecutor(max_workers=args.max_workers) as executor:
        futures = {executor.submit(check_notebook_syntax, nb_path): nb_path for nb_path in notebook_files}
        
        for future in as_completed(futures):
            notebook_path, success, message = future.result()
            notebook_name = os.path.basename(notebook_path)
            
            if success:
                successful.append((notebook_name, message))
                print(f"✅ {notebook_name}: {message}")
            else:
                failed.append((notebook_name, message))
                print(f"❌ {notebook_name}: {message}")
    
    # Print summary
    print("\n" + "="*80)
    print(f"SYNTAX CHECK SUMMARY: {len(successful)} succeeded, {len(failed)} failed")
    print("="*80)
    
    if failed:
        print("\nNOTEBOOKS WITH SYNTAX ERRORS:")
        for name, error in failed:
            print(f"❌ {name}")
            # Print the first few lines of the error message
            error_lines = error.split('\n')[:5]  # Limit to first 5 lines
            for line in error_lines:
                print(f"   {line}")
            if len(error_lines) < len(error.split('\n')):
                print(f"   ... (truncated)")
            print()
    
    if successful:
        print(f"\n{len(successful)} NOTEBOOKS WITH NO SYNTAX ERRORS:")
        # Print in columns to save space
        col_width = max(len(name) for name, _ in successful) + 2
        cols = 3  # Number of columns
        for i in range(0, len(successful), cols):
            row = successful[i:i+cols]
            print(''.join(f"✅ {name:<{col_width}}" for name, _ in row))
    
    # Return non-zero exit code if any notebooks failed
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
