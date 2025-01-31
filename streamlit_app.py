import streamlit as st
import pandas as pd
import json

# Set page config MUST be the first Streamlit command
st.set_page_config(layout="wide")

# Load and prepare data
file_path = "matrix explained.xlsx"
try:
    df = pd.read_excel(file_path, index_col=0)
    df.index = df.index.str.strip()
    df.columns = ['Processes', 'Products', 'Tools']
    row_names = df.index.tolist()
    column_names = df.columns.tolist()
except Exception as e:
    st.error(f"Error loading Excel file: {e}")
    st.stop()

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
    "Roles": ["Analyst", "Architect", "Consultant", "Director", 
             "Engineer", "Manager", "President", "Vice President"],
}

# Configure cell quotes
cell_quotes = {
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
                 "We can change the design this is just a prototype, we can make it more aesthetically pleasing and colorful!"],
        "filters": {"Roles": ["Consultant"]}
    },
    "4,1": {
        "quotes": ["Leadership should drive flexibility initiatives",
                 "Regular review meetings with product teams"],
        "filters": {"Organisation Types": ["Client"]}
    }
}

# Streamlit UI
st.title("Flexibility Matrix Explorer")

# Filter selection
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    main_filter = st.selectbox(
        "Select Main Filter",
        [""] + list(filters_data.keys()),
        key="main_filter"
    )

with col2:
    subfilter_options = [""] + filters_data.get(main_filter, []) if main_filter else [""]
    subfilter = st.selectbox(
        "Select Subfilter",
        subfilter_options,
        key="subfilter"
    )

with col3:
    st.write("")  # Vertical spacing
    st.write("")
    apply_pressed = st.button("Apply Filters")

# Initialize session state
if 'applied_filters' not in st.session_state:
    st.session_state.applied_filters = None

# Handle filter application
if apply_pressed:
    if main_filter and subfilter:
        st.session_state.applied_filters = (main_filter, subfilter)
    else:
        st.warning("Please select both a main filter and subfilter before applying")
        st.session_state.applied_filters = None

# Calculate highlighted cells based on applied filters
highlighted_cells = []
if st.session_state.applied_filters:
    main_filter, subfilter = st.session_state.applied_filters
    st.write(f"Applied Filters: {main_filter} -> {subfilter}")  # Debug
    for coord, data in cell_quotes.items():
        if data["filters"].get(main_filter) and subfilter in data["filters"][main_filter]:
            highlighted_cells.append(coord)
            st.write(f"Highlighted Cell: {coord}")  # Debug

# Prepare data for HTML component
matrix_data = {
    "column_names": column_names,
    "row_names": row_names,
    "definitions": definitions,
    "cell_quotes": cell_quotes,
    "highlighted_cells": highlighted_cells,
}

# HTML/JavaScript component
html = f'''
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ 
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100vh;
            overflow: hidden;
        }}
        
        .matrix-wrapper {{
            width: 100%;
            height: 100%;
            overflow: auto;
        }}

        table {{
            border-collapse: collapse;
            table-layout: fixed;
            width: 100%;
            min-width: 1000px;
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
            white-space: normal !important;
            word-wrap: break-word;
            min-width: 150px;
        }}

        th:first-child, td:first-child {{
            position: sticky;
            left: 0;
            z-index: 2;
            background: #f8f9fa;
            min-width: 200px;
        }}

        th {{
            position: sticky;
            top: 0;
            z-index: 3;
            background: #f8f9fa;
        }}

        .highlighted {{
            background: #e3f2fd !important; 
            border: 2px solid #2196f3 !important;
        }}

        .tooltip {{
            position: absolute;
            background: white;
            border: 1px solid #ddd;
            padding: 10px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            z-index: 9999;
            max-width: 300px;
        }}
    </style>
</head>
<body>
    <div class="matrix-wrapper">
        <table id="matrixTable"></table>
    </div>

    <script>
        const data = {json.dumps(matrix_data, ensure_ascii=False)};

        function buildMatrix() {{
            const table = document.getElementById('matrixTable');
            table.innerHTML = '';

            // Create header row
            let headerRow = '<tr><th>Factors</th>';
            data.column_names.forEach(col => {{
                headerRow += `<th>${{col}}</th>`;
            }});
            headerRow += '</tr>';
            table.innerHTML = headerRow;

            // Create data rows
            data.row_names.forEach((rowName, rowIndex) => {{
                let rowHtml = `<tr><td>${{rowName}}</td>`;
                data.column_names.forEach((colName, colIndex) => {{
                    const coord = `${{rowIndex}},${{colIndex}}`;
                    const content = data.definitions[rowName][colName];
                    const isHighlighted = data.highlighted_cells.includes(coord);
                    const quotes = data.cell_quotes[coord]?.quotes || [];

                    rowHtml += `
                        <td class="${{isHighlighted ? 'highlighted' : ''}}"
                            data-quotes='${{JSON.stringify(quotes)}}'
                            onmouseover="${{isHighlighted ? 'showTooltip(event)' : ''}}"
                            onmouseout="${{isHighlighted ? 'hideTooltip()' : ''}}">
                            ${{content}}
                        </td>
                    `;
                }});
                rowHtml += '</tr>';
                table.innerHTML += rowHtml;
            }});

            adjustTableWidth();
        }}

        function adjustTableWidth() {{
            const table = document.getElementById('matrixTable');
            const container = document.querySelector('.matrix-wrapper');
            if (table && container) {{
                table.style.width = '100%';
                container.style.width = '100%';
            }}
        }}

        function showTooltip(event) {{
            const quotes = JSON.parse(event.target.dataset.quotes);
            if (!quotes.length) return;

            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.innerHTML = `<ul>${{quotes.map(q => `<li>${{q}}</li>`).join('')}}</ul>`;

            document.body.appendChild(tooltip);
            const rect = event.target.getBoundingClientRect();
            tooltip.style.left = `${{rect.right + 5}}px`;
            tooltip.style.top = `${{rect.top}}px`;
        }}

        function hideTooltip() {{
            const tooltips = document.getElementsByClassName('tooltip');
            while(tooltips[0]) tooltips[0].remove();
        }}

        // Initial build and dynamic resizing
        buildMatrix();
        window.addEventListener('resize', adjustTableWidth);
        window.onload = adjustTableWidth;
    </script>
</body>
</html>'''

# Show disclaimer only when filters are applied
if st.session_state.applied_filters:
    st.info("ℹ️ Hover over highlighted cells to view corresponding quotes")

# Render the component
st.components.v1.html(html, height=800, scrolling=True)
