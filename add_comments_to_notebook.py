#!/usr/bin/env python
import json
import sys

def add_comments_to_notebook(notebook_path, output_path):
    """
    Add descriptive comments to a Jupyter notebook.
    
    Args:
        notebook_path: Path to the original notebook
        output_path: Path where the modified notebook will be saved
    """
    # Read the notebook
    with open(notebook_path, 'r') as f:
        notebook = json.load(f)
    
    # Define section descriptions
    section_descriptions = {
        0: "# Pandas 102 - Advanced Pandas Operations\n\nThis notebook covers essential pandas operations and techniques for data manipulation and analysis.",
        1: "# Setup and Configuration\n\nImporting pandas and configuring display options to show all columns, rows, and cell contents.",
        2: "# Creating a DataFrame\n\nCreating a sample DataFrame with different data types including float, timestamp, categorical, and object.",
        3: "# Basic DataFrame Operations\n\nDisplaying the first few rows of the DataFrame using head().",
        4: "# Viewing Last Rows\n\nDisplaying the last few rows of the DataFrame using tail().",
        5: "# Random Sampling\n\nSelecting random samples from the DataFrame using sample().",
        6: "# Index Information\n\nAccessing and displaying the DataFrame's index.",
        7: "# Column Information\n\nAccessing and displaying the DataFrame's columns.",
        8: "# Data Types\n\nChecking the data types of each column in the DataFrame using dtypes.",
        9: "# Statistical Summary\n\nGenerating a statistical summary of the DataFrame using describe().",
        10: "# Transposing Data\n\nTransposing the DataFrame to switch rows and columns using T.",
        11: "# Viewing Data\n\nDisplaying the entire DataFrame.",
        12: "# Sorting Data\n\nSorting the DataFrame by specific columns using sort_values().",
    }
    
    # Add comments to markdown cells
    cell_index = 0
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'markdown' and i == 0:
            # Replace the first markdown cell with our title and description
            cell['source'] = [section_descriptions[0]]
        elif cell['cell_type'] == 'code':
            # For code cells, add a markdown cell before with description if available
            if cell_index + 1 in section_descriptions:
                # Create a new markdown cell with the description
                markdown_cell = {
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': [section_descriptions[cell_index + 1]]
                }
                # Insert the markdown cell before the code cell
                notebook['cells'].insert(i, markdown_cell)
                cell_index += 1
    
    # Save the modified notebook
    with open(output_path, 'w') as f:
        json.dump(notebook, f, indent=1)
    
    print(f"Successfully added comments to {notebook_path} and saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python add_comments_to_notebook.py <input_notebook_path> <output_notebook_path>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    add_comments_to_notebook(input_path, output_path)
