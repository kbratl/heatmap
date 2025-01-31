import streamlit as st
import pandas as pd
import json

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
                 "We might change the design this is just a prototype..."],
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
    for coord, data in cell_quotes.items():
        if data["filters"].get(main_filter) and subfilter in data["filters"][main_filter]:
            highlighted_cells.append(coord)

# Prepare data for HTML component
matrix_data = {
    "column_names": column_names,
    "row_names": row_names,
    "definitions": definitions,
    "cell_quotes": cell_quotes,
    "highlighted_cells": highlighted_cells,
}

# HTML/JavaScript component with full-width matrix
html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ 
            margin: 0;
            padding: 0;
            width: 100%;
            min-width: fit-content;
        }}
        .matrix-wrapper {{
            width: 100%;
            overflow: visible;
        }}
        table {{
            border-collapse: collapse;
            width: auto;
            min-width: 100%;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 15px;
            text-align: left;
            min-width: 800px;  /* Wider minimum column width */
            white-space: normal;
            background: white;
            position: relative;
            font-size: 16px;
        }}
        th:first-child {{
            position: sticky;
            left: 0;
            z-index: 3;
            background: #f8f9fa;
            min-width: 850px;  /* Extra wide first column */
            font-size: 18px;
        }}
        td:first-child {{
            position: sticky;
            left: 0;
            z-index: 2;
            background: #f8f9fa;
            font-size: 16px;
        }}
        th {{
            position: sticky;
            top: 0;
            z-index: 3;
            background: #f8f9fa;
            font-size: 18px;
        }}
        .matrix-container {{
            width: fit-content;
            min-width: 100%;
        }}
        .highlighted {{
            background: #e3f2fd !important; 
            border: 2px solid #2196f3 !important;
        }}
        .tooltip {{
            position: fixed;
            background: #fff;
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            max-width: 400px;
            z-index: 1000;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="matrix-wrapper">
        <div class="matrix-container">
            <table id="matrixTable"></table>
        </div>
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
                            <div class="cell-content">${{content}}</div>
                        </td>
                    `;
                }});
                rowHtml += '</tr>';
                table.innerHTML += rowHtml;
            }});
            
            // Set explicit widths
            const container = document.querySelector('.matrix-container');
            container.style.width = table.offsetWidth + 'px';
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
        
        // Initial build
        buildMatrix();
        window.addEventListener('resize', buildMatrix);
    </script>
</body>
</html>
"""

# Show disclaimer only when filters are applied
if st.session_state.applied_filters:
    st.info("ℹ️ Hover over highlighted cells to view corresponding quotes")

# Render the component
st.components.v1.html(html, height=3000)
