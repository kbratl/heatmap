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

html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Flexibility Matrix Explorer</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .filters { margin-bottom: 20px; padding: 10px; background: #f5f5f5; }
        select { margin-right: 15px; padding: 5px; }
        button { padding: 5px 15px; background: #007bff; color: white; border: none; cursor: pointer; }
        button:hover { background: #0056b3; }
        table { border-collapse: collapse; margin-top: 20px; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background: #f8f9fa; }
        .dimmed { background: #f8f9fa; color: #999; border-color: #eee; }
        .highlighted { background: #e3f2fd; border: 2px solid #2196f3; }
        .tooltip {
            position: absolute;
            background: #fff;
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            max-width: 300px;
            z-index: 1000;
        }
    </style>
</head>
<body>
    <div class="filters">
        <select id="mainFilter">
            <option value="">Select Main Filter</option>
            {% for filter in filters_data %}
                <option value="{{ filter }}">{{ filter }}</option>
            {% endfor %}
        </select>
        
        <select id="subFilter">
            <option value="">Select Subfilter</option>
        </select>
        
        <button onclick="applyFilters()">Apply Filters</button>
    </div>

    <table>
        <tr>
            <th>Factors</th>
            {% for col in column_names %}
                <th>{{ col }}</th>
            {% endfor %}
        </tr>
        {% for row_idx in range(row_names|length) %}
        <tr>
            <td>{{ row_names[row_idx] }}</td>
            {% for col_idx in range(column_names|length) %}
                <td class="cell"
                    data-row="{{ row_idx }}"
                    data-col="{{ col_idx }}"
                    data-quotes='{{ cell_quotes.get("%d,%d"|format(row_idx, col_idx), {"quotes": []})|tojson }}'>
                    {{ definitions[row_names[row_idx]][column_names[col_idx]] }}
                </td>
            {% endfor %}
        </tr>
        {% endfor %}
    </table>

    <script>
        document.getElementById('mainFilter').addEventListener('change', function() {
            const filter = this.value;
            fetch('/get_subfilters', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filter: filter })
            }).then(res => res.json()).then(data => {
                const subFilter = document.getElementById('subFilter');
                subFilter.innerHTML = '<option value="">Select Subfilter</option>';
                data.subfilters.forEach(sub => {
                    const opt = document.createElement('option');
                    opt.value = sub;
                    opt.textContent = sub;
                    subFilter.appendChild(opt);
                });
            });
        });

        function applyFilters() {
            const filter = document.getElementById('mainFilter').value;
            const subfilter = document.getElementById('subFilter').value;
            
            fetch('/filter_matrix', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filter: filter, subfilter: subfilter })
            }).then(res => res.json()).then(data => {
                document.querySelectorAll('.cell').forEach(cell => {
                    const cellKey = `${cell.dataset.row},${cell.dataset.col}`;
                    if (data.highlighted_cells.includes(cellKey)) {
                        cell.classList.add('highlighted');
                        cell.classList.remove('dimmed');
                    } else {
                        cell.classList.add('dimmed');
                        cell.classList.remove('highlighted');
                    }
                });
            });
        }

        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        document.body.appendChild(tooltip);

        document.querySelectorAll('.cell').forEach(cell => {
            cell.addEventListener('mouseover', function(e) {
                const quotes = JSON.parse(this.dataset.quotes).quotes;
                if (quotes.length > 0) {
                    tooltip.innerHTML = '<ul>' + 
                        quotes.map(q => `<li>${q}</li>`).join('') + 
                        '</ul>';
                    tooltip.style.display = 'block';
                    tooltip.style.left = `${e.pageX + 15}px`;
                    tooltip.style.top = `${e.pageY + 15}px`;
                }
            });

            cell.addEventListener('mouseout', () => {
                tooltip.style.display = 'none';
            });
        });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(
        html_template,
        filters_data=filters_data,
        row_names=row_names,
        column_names=column_names,
        definitions=definitions,
        cell_quotes=cell_quotes
    )

@app.route("/get_subfilters", methods=["POST"])
def get_subfilters():
    selected_filter = request.json.get("filter")
    return jsonify({"subfilters": filters_data.get(selected_filter, [])})

@app.route("/filter_matrix", methods=["POST"])
def filter_matrix():
    filter_type = request.json.get("filter")
    subfilter = request.json.get("subfilter")
    
    highlighted = []
    for coord, data in cell_quotes.items():
        if filter_type in data.get("filters", {}):
            if subfilter in data["filters"][filter_type]:
                highlighted.append(coord)
    
    return jsonify({"highlighted_cells": highlighted})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
