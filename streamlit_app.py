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
        if main_filter in data.get("filters", {}):
            if subfilter in data["filters"][main_filter]:
                highlighted_cells.append(coord)

# Show disclaimer only when filters are applied
if st.session_state.applied_filters:
    st.info("ℹ️ Hover over highlighted cells to view corresponding quotes")

# Prepare data for HTML component
matrix_data = {
    "column_names": column_names,
    "row_names": row_names,
    "definitions": definitions,
    "cell_quotes": cell_quotes,
    "highlighted_cells": highlighted_cells,
}

# Update the JavaScript section in the HTML component:
html = f"""
<!DOCTYPE html>
<html>
<head>
    <!-- Keep the existing CSS styles -->
</head>
<body>
    <div class="matrix-container">
        <table id="matrixTable"></table>
    </div>

    <script>
        const data = {json.dumps(matrix_data, ensure_ascii=False)};
        
        function buildMatrix() {{
            const table = document.getElementById('matrixTable');
            table.innerHTML = '';
            
            // Create header
            let headerRow = '<tr><th>Factors</th>' + 
                data.column_names.map(col => `<th>${{col}}</th>`).join('') + '</tr>';
            table.innerHTML = headerRow;
            
            // Create rows
            data.row_names.forEach((rowName, rowIdx) => {{
                let rowHtml = `<tr><td>${{rowName}}</td>`;
                data.column_names.forEach((col, colIdx) => {{
                    const coord = `${{rowIdx}},${{colIdx}}`;
                    const content = data.definitions[rowName][col];
                    const quotes = data.cell_quotes[coord]?.quotes || [];
                    const isHighlighted = data.highlighted_cells.includes(coord);
                    const cellClass = isHighlighted ? 'highlighted' : 'dimmed';
                    
                    rowHtml += `
                        <td class="${{cellClass}}"
                            data-quotes='${{JSON.stringify(quotes)}}'
                            onmouseover="showTooltip(event)"
                            onmouseout="hideTooltip()">
                            ${{content}}
                        </td>
                    `;
                }});
                table.innerHTML += rowHtml + '</tr>';
            }});
        }}

        // Rest of the JavaScript functions remain the same
        function showTooltip(event) {{
            const quotes = JSON.parse(event.target.dataset.quotes);
            if (!quotes.length) return;
            
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.innerHTML = `<ul>${{quotes.map(q => `<li>${{q}}</li>`).join('')}}</ul>`;
            
            document.body.appendChild(tooltip);
            tooltip.style.left = `${{event.pageX + 15}}px`;
            tooltip.style.top = `${{event.pageY + 15}}px`;
        }}
        
        function hideTooltip() {{
            const tooltips = document.getElementsByClassName('tooltip');
            while(tooltips[0]) tooltips[0].remove();
        }}
        
        // Initial build
        buildMatrix();
    </script>
</body>
</html>
"""

# The rest of your Streamlit code remains unchanged
# Render the component
st.components.v1.html(html, height=1200)
