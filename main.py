from flask import Flask, render_template_string, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Load and prepare data
file_path = "matrix_explained.xlsx"
try:
    df = pd.read_excel(file_path, index_col=0)
    df.index = df.index.str.strip()
    df.columns = ['Processes', 'Products', 'Tools']
    row_names = df.index.tolist()
    column_names = df.columns.tolist()
except Exception as e:
    raise RuntimeError(f"Error loading Excel file: {e}")

# Build definitions dictionary
definitions = {
    row: {col: str(df.at[row, col]) for col in column_names}
    for row in row_names
}

# Configure filters
filters_data = {
    "Phases": ["Monitoring", "Pre-Contract", "Planning", "Execution", "Delivery"],
    "Investment Types": ["Public", "Private", "PPP"],
    "Contract Types": ["Fixed Price", "Time & Material", "Cost Plus"],
    "Organisation Types": ["Client", "Contractor", "Consultant"],
    "Roles": ["Analyst", "Architect", "Consultant", "Director", "Engineer", "Manager", "President", "Vice President"],
}

# Configure cell quotes
cell_quotes = {
    "0,0": {  # Pre-Contract Motivations x Processes
        "quotes": ["Chocolate", "Yes we can make a dynamic heatmap matrix work :)"],
        "filters": {"Roles": ["Consultant"]}
    },
    "6,1": {  # Leadership commitment x Products
        "quotes": ["I think deepseek's R1 model is better for fixing code errors", 
                 "An americano with an extra shot"],
        "filters": {"Roles": ["Consultant"]}
    },
    "9,2": {  # Long-term perspective x Tools
        "quotes": ["Will we display all the quotes", 
                 "We might change the design this is just a prototype, we can make it more aesthetic and colorful!"],
        "filters": {"Roles": ["Consultant"]}
    }
}

# ... [Keep the same HTML template and routes from previous answer] ...

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
