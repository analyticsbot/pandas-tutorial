## Pandas Tutorial: Essential Functions for Data Analysis

Welcome to the Pandas Tutorial! This project breaks down the official [pandas documentation](https://pandas.pydata.org/pandas-docs/version/1.4/pandas.pdf) into simple, easy-to-understand Jupyter notebooks. I took that PDF and broke down in sections of approximately 25 pages each. Each notebook focuses on specific pandas functions found within these sections. They are stored in the [pandas_pdf](./pandas_pdf) directory.

### How It's Organized

- Each notebook is named `part_XXX.ipynb` where `XXX` represents the section number
- Every notebook covers specific pandas functions with simple examples
- All examples include clear explanations with minimal technical jargon
- Code is ready to run and experiment with. Note: some functions may not be implemented yet since this is not the exact PDF version.

### What You'll Learn

- How to create and manipulate DataFrames and Series
- Essential data cleaning and transformation techniques
- Data analysis methods with practical examples
- Visualization techniques using pandas
- Time series analysis capabilities
- Advanced pandas features for real-world data tasks

### Folder Structure

- notebooks/
    - part_XXX.ipynb - Jupyter notebooks with pandas examples and explanations
- pandas_pdf/
    - part_XXX.pdf - Original PDF sections from the pandas documentation
    - pandas.pdf - The complete pandas documentation PDF

### How to Use This Tutorial

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

### Key Topics Covered

- DataFrame and Series creation and manipulation
- Data selection, filtering and cleaning
- Grouping, aggregation and pivoting
- Time series analysis
- Data visualization
- Advanced pandas features

### How to Contribute

If you see a gap in the tutorial, or can improve any of the examples, please open a pull request.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Enjoy learning pandas in a simple, practical way!
