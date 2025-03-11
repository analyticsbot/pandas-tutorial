# Pandas Tutorial: Essential Functions for Data Analysis

Welcome to the Pandas Tutorial! This project breaks down the official [pandas documentation](https://pandas.pydata.org/pandas-docs/version/1.4/pandas.pdf) into simple, easy-to-understand Jupyter notebooks.

## About This Project

This tutorial is based on the pandas documentation PDF (version 1.4), which has been split into sections of approximately 25 pages each. Each notebook focuses on specific pandas functions found within these sections.

## How It's Organized

- Each notebook is named `part_X.ipynb` where X represents the section number
- Every notebook covers specific pandas functions with simple examples
- All examples include clear explanations with minimal technical jargon
- Code is ready to run and experiment with

## What You'll Learn

- How to create and manipulate DataFrames and Series
- Essential data cleaning and transformation techniques
- Data analysis methods with practical examples
- Visualization techniques using pandas
- Time series analysis capabilities
- Advanced pandas features for real-world data tasks

## How to Use This Tutorial

1. Clone this repository
2. Set up a virtual environment and install dependencies:
   ```bash
   # Create a virtual environment
   python -m venv venv
   
   # Activate the virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   # venv\Scripts\activate
   
   # Install required packages
   pip install -r requirements.txt
   ```
3. Start Jupyter Notebook:
   ```bash
   jupyter notebook
   ```
4. Start with `part_001.ipynb` and progress through the numbered notebooks
5. Run the code cells to see the functions in action
6. Modify examples to experiment with your own data

Each notebook is designed to be independent, so you can also jump to specific topics you're interested in.

## Key Topics Covered

- DataFrame and Series creation and manipulation
- Data selection, filtering and cleaning
- Grouping, aggregation and pivoting
- Time series analysis
- Data visualization
- Advanced pandas features

## Utility Scripts

### Syntax Checking

This repository includes a script to check all notebooks for syntax errors without executing them:

```bash
# Activate the virtual environment first
source venv/bin/activate

# Run the syntax check script
python run_all_notebooks.py
```

This script will scan all Jupyter notebooks in the repository and report any Python syntax errors found in code cells.

Enjoy learning pandas in a simple, practical way!
