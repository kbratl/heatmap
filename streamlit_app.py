from flask import Flask, render_template_string, request, jsonify
from pyngrok import ngrok
import pandas as pd
import os

app = Flask(__name__)

# Configuration
CONFIG = {
    "app_title": "Flexibility Contributing Factors Heatmap Matrix",
    "excel_file": "matrix explained.xlsx",
    "filters": {
        "Phases": ["Monitoring", "Pre-Contract", "Planning", "Execution", "Delivery"],
        "Investment Types": ["Public", "Private", "PPP"],
        "Contract Types": ["Fixed Price", "Time & Material", "Cost Plus"],
        "Organisation Types": ["Client", "Contractor", "Consultant"],
        "Roles": ["Analyst", "Architect", "Consultant", "Director", "Engineer", 
                 "Manager", "President", "Vice President"],
    },
    "cell_quotes": {
        "0,0": {
            "quotes": ["Chocolate", "Yes we can make a dynamic heatmap matrix work :)"],
            "filters": {"Roles": ["Consultant"]}
        },
        "6,1": {
            "quotes": ["I think deepseek's R1 model is better for fixing code errors", 
                      "An americano with an extra shot"],
            "filters": {"Roles": ["Consultant"]}
        },
        "9,2": {
            "quotes": ["Will we display all the quotes", 
                      "We might change the design this is just a prototype"],
            "filters": {"Roles": ["Consultant"]}
        }
    },
    "colors": {
        "primary": "#1a73e8",
        "secondary": "#f8f9fa",
        "highlight": "#e8f0fe",
        "border": "#dadce0"
    }
}

# Data Loading
def load_data():
    try:
        df = pd.read_excel(CONFIG["excel_file"], index_col=0)
        df.index = df.index.str.strip()
        df.columns = ['Processes', 'Products', 'Tools']
        return df
    except Exception as e:
        raise RuntimeError(f"Error loading Excel file: {e}")

# Initialize data
df = load_data()
row_names = df.index.tolist()
column_names = df.columns.tolist()
definitions = {row: {col: str(df.at[row, col]) for col in column_names} for row in row_names}

# HTML Template
HTML_TEMPLATE = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{CONFIG['app_title']}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 20px;
            color: #202124;
        }}
        .header {{
            padding: 20px;
            background: {CONFIG['colors']['primary']};
            color: white;
            margin-bottom: 25px;
            border-radius: 4px;
        }}
        .filters {{
            margin-bottom: 25px;
            padding: 15px;
            background: {CONFIG['colors']['secondary']};
            border-radius: 4px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }}
        select {{
            margin-right: 15px;
            padding: 8px 12px;
            border: 1px solid {CONFIG['colors']['border']};
            border-radius: 4px;
            min-width: 200px;
        }}
        button {{
            padding: 8px 20px;
            background: {CONFIG['colors']['primary']};
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.2s;
        }}
        button:hover {{
            background: #1557b0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            background: white;
        }}
        th, td {{
            border: 1px solid {CONFIG['colors']['border']};
            padding: 15px;
            text-align: left;
            min-width: 250px;
        }}
        th {{
            background: {CONFIG['colors']['primary']};
            color: white;
            position: sticky;
            top: 0;
        }}
        .dimmed {{
            background: {CONFIG['colors']['secondary']};
            color: #5f6368;
        }}
        .highlighted {{
            background: {CONFIG['colors']['highlight']};
            border: 2px solid {CONFIG['colors']['primary']} !important;
            position: relative;
        }}
        .tooltip {{
            position: fixed;
            background: white;
            border: 1px solid {CONFIG['colors']['border']};
            padding: 15px;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            max-width: 350px;
            z-index: 1000;
            pointer-events: none;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{CONFIG['app_title']}</h1>
    </div>
    
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
            <td><strong>{{ row_names[row_idx] }}</strong></td>
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
        // Filter Handling
        const mainFilter = document.getElementById('mainFilter');
        const subFilter = document.getElementById('subFilter');
        
        mainFilter.addEventListener('change', async () => {{
            const response = await fetch('/get_subfilters', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ filter: mainFilter.value }})
            }});
            const {{ subfilters }} = await response.json();
            
            subFilter.innerHTML = '<option value="">Select Subfilter</option>' + 
                subfilters.map(sub => `<option value="${{sub}}">${{sub}}</option>`).join('');
        }});

        // Apply Filters
        async function applyFilters() {{
            const response = await fetch('/filter_matrix', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{
                    filter: mainFilter.value,
                    subfilter: subFilter.value
                }})
            }});
            const {{ highlighted_cells }} = await response.json();
            
            document.querySelectorAll('.cell').forEach(cell => {{
                const cellKey = `${{cell.dataset.row}},${{cell.dataset.col}}`;
                cell.className = highlighted_cells.includes(cellKey)
                    ? 'cell highlighted'
                    : 'cell dimmed';
            }});
        }}

        // Tooltip System
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        document.body.appendChild(tooltip);

        document.querySelectorAll('.cell').forEach(cell => {{
            cell.addEventListener('mousemove', (e) => {{
                const quotes = JSON.parse(cell.dataset.quotes).quotes;
                if (quotes.length) {{
                    tooltip.innerHTML = `<div class="tooltip-content">
                        <h4>${{cell.closest('tr').firstChild.textContent}} → ${{cell.closest('td').parentNode.children[cell.cellIndex].firstChild.textContent}}</h4>
                        <ul>${{quotes.map(q => `<li>${{q}}</li>`).join('')}}</ul>
                    </div>`;
                    tooltip.style.display = 'block';
                    tooltip.style.left = `${{e.pageX + 15}}px`;
                    tooltip.style.top = `${{e.pageY + 15}}px`;
                }}
            }});

            cell.addEventListener('mouseleave', () => {{
                tooltip.style.display = 'none';
            }});
        }});
    </script>
</body>
</html>
"""

# Flask Routes
@app.route("/")
def index():
    return render_template_string(
        HTML_TEMPLATE,
        filters_data=CONFIG["filters"],
        row_names=row_names,
        column_names=column_names,
        definitions=definitions,
        cell_quotes=CONFIG["cell_quotes"]
    )

@app.route("/get_subfilters", methods=["POST"])
def get_subfilters():
    selected_filter = request.json.get("filter")
    return jsonify({"subfilters": CONFIG["filters"].get(selected_filter, [])})

@app.route("/filter_matrix", methods=["POST"])
def filter_matrix():
    filter_type = request.json.get("filter")
    subfilter = request.json.get("subfilter")
    
    highlighted = [
        coord for coord, data in CONFIG["cell_quotes"].items()
        if subfilter in data.get("filters", {}).get(filter_type, [])
    ]
    
    return jsonify({"highlighted_cells": highlighted})

# Main Execution
if __name__ == "__main__":
    public_url = ngrok.connect(5000)
    print(f" * ngrok tunnel: {public_url}")
    app.run(host='0.0.0.0', port=5000)
