from flask import Flask, render_template_string, request, jsonify
import pandas as pd
import os

app = Flask(__name__)


# Ensure the file exists
file_path = "matrix explained.xlsx"
if not os.path.exists(file_path):
    print(f"❌ ERROR: File '{file_path}' not found. Please upload it again.")
    exit()

# Try loading the Excel file with 'openpyxl'
try:
    df = pd.read_excel(file_path, index_col=0, engine='openpyxl')  # Removed 'encoding' argument
    df.index = df.index.astype(str).str.strip().str.lower().str.replace(" ", "_")
    df.columns = df.columns.astype(str).str.strip().str.lower().str.replace(" ", "_")
except Exception as e:
    print(f"❌ ERROR Loading Excel file: {e}")
    exit()

# Extract row and column names
row_names = df.index.tolist()
column_names = df.columns.tolist()

# Build dictionary for definitions
definitions = {
    row_name: {col_name: str(df.at[row_name, col_name]) for col_name in column_names}
    for row_name in row_names
}

# Example quotes for specific intersections
cell_quotes = {
    "0,0": ["chocolate", "let's make it work"],
    "1,1": ["watching a streamer and singing along with him", "laylaylom"],
    "2,2": ["let's try quotes with long sentence whether it would be able to display", "i enjoy a challenge"],
}

# Filters
filters_data = {
    "Phases": ["Monitoring", "Pre-Contract", "Planning", "Execution", "Delivery"],
    "Investment Types": ["Public", "Private", "PPP"],
    "Contract Types": ["Fixed Price", "Time & Material", "Cost Plus"],
    "Organisation Types": ["Client", "Contractor", "Consultant"],
    "Roles": ["Analyst", "Architect", "Consultant", "Director", "Engineer", "Manager", "President", "Vice President"],
}

@app.route("/")
def index():
    return render_template_string(
        """<!DOCTYPE html>
        <html>
        <head>
            <title>Matrix Visualization</title>
        </head>
        <body>
            <h1>Matrixx Visualization</h1>
            <p>Flask App is Running</p>
        </body>
        </html>""",
        filters_data=filters_data,
        row_names=row_names,
        column_names=column_names,
        definitions=definitions,
        enumerate=enumerate
    )

@app.route("/get_subfilters", methods=["POST"])
def get_subfilters():
    selected_filter = request.json.get("filter")
    subfilters = filters_data.get(selected_filter, [])
    return jsonify({"subfilters": subfilters})

@app.route("/filter_matrix", methods=["POST"])
def filter_matrix():
    selected_filter = request.json.get("filter")
    selected_subfilter = request.json.get("subfilter")

    filtered_cells = {}
    if selected_filter == "Roles" and selected_subfilter.lower() == "consultant":
        filtered_cells = {
            "0,0": cell_quotes.get("0,0", []),
            "1,1": cell_quotes.get("1,1", []),
            "2,2": cell_quotes.get("2,2", []),
        }

    return jsonify({"highlighted_cells": filtered_cells})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)  # Use Replit's built-in hosting
