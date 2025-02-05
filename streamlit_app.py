import streamlit as st
import pandas as pd
import json
import math

# Set page config MUST be the first Streamlit command
st.set_page_config(layout="wide")

# Load and prepare data
file_path = "matrix explained.xlsx"
try:
    base_df = pd.read_excel(file_path, index_col=0)
    base_df.index = base_df.index.str.strip()
    base_df.columns = ['Processes', 'Products', 'Tools']
    row_names = base_df.index.tolist()
    column_names = base_df.columns.tolist()
except Exception as e:
    st.error(f"Error loading Excel file: {e}")
    st.stop()

# Configure dynamic percentages for different filters
dynamic_percentages = {
    ('Roles', 'Consultant'): {
        "Pre-Contract Motivations": {"Processes": 32, "Products": 8, "Tools": 13},
        "Interpretation Competence": {"Processes": 27, "Products": 5, "Tools": 8},
        "Leadership commitment to being flexible": {"Processes": 42, "Products": 10, "Tools": 13},
        "Experimentation and learning": {"Processes": 9, "Products": 12, "Tools": 13},
        "Defining Flexibility Related Project Objectives": {"Processes": 19, "Products": 8, "Tools": 25},
        "Long-term Perspective": {"Processes": 13, "Products": 11, "Tools": 16},
    },
    # Add other filter combinations here
}

# Configure filters
filters_data = {
    "Phases": ["Monitoring", "Pre-Contract", "Planning", "Execution", "Delivery"],
    "Investment Types": ["Public", "Private", "PPP"],
    "Contract Types": ["Fixed Price", "Time & Material", "Cost Plus"],
    "Organisation Types": ["Contractor", "Client", "Consultant"],
    "Roles": ["Analyst", "Architect", "Consultant", "Director", 
             "Engineer", "Manager", "President", "Vice President"],
}

# Configure cell quotes
cell_quotes = {
    "0,0": {"quotes": ["We can change the design...", "Yes we can..."], "filters": {"Roles": ["Consultant"]}},
    "7,1": {"quotes": ["I do not know...", "An americano..."], "filters": {"Roles": ["Consultant"]}},
    "6,1": {"quotes": ["I think deepseek...", "An americano..."], "filters": {"Roles": ["Consultant"]}},
    "9,2": {"quotes": ["Will we display...", "Chocolate"], "filters": {"Roles": ["Consultant"]}},
    "4,1": {"quotes": ["I tried only...", "Dueting with..."], "filters": {"Roles": ["Consultant"]}},
    "8,2": {"quotes": ["Long-term planning...", "Just writing..."], "filters": {"Roles": ["Consultant"]}},
}

# Streamlit UI
st.title("Flexibility Contributing Factors Matrix")

# Filter selection
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    main_filter = st.selectbox("Select Main Filter", [""] + list(filters_data.keys()), key="main_filter")
with col2:
    subfilter_options = [""] + filters_data.get(main_filter, []) if main_filter else [""]
    subfilter = st.selectbox("Select Subfilter", subfilter_options, key="subfilter")
with col3:
    st.write("")
    apply_pressed = st.button("Apply Filters")

# Initialize session state
if 'applied_filters' not in st.session_state:
    st.session_state.applied_filters = None
if 'current_df' not in st.session_state:
    st.session_state.current_df = base_df.copy()

# Handle filter application
if apply_pressed:
    if main_filter and subfilter:
        st.session_state.applied_filters = (main_filter, subfilter)
        # Apply dynamic percentages if available
        filter_key = (main_filter, subfilter)
        percentages = dynamic_percentages.get(filter_key, {})
        
        # Create a fresh copy of the base DataFrame
        filtered_df = base_df.copy()
        
        # Apply percentages to the DataFrame
        for row, cols in percentages.items():
            for col, percent in cols.items():
                filtered_df.at[row, col] = f"{percent}%|{base_df.at[row, col]}"
        
        st.session_state.current_df = filtered_df
    else:
        st.warning("Please select both a main filter and subfilter before applying")
        st.session_state.applied_filters = None

# Build definitions dictionary from current DF
definitions = {
    row: {col: str(st.session_state.current_df.at[row, col]) for col in column_names}
    for row in row_names
}

# Calculate highlighted cells based on applied filters
filtered_quotes = {}
highlighted_cells = []
if st.session_state.applied_filters:
    main_filter, subfilter = st.session_state.applied_filters
    
    for coord, data in cell_quotes.items():
        if main_filter in data["filters"] and subfilter in data["filters"][main_filter]:
            highlighted_cells.append(coord)
            filtered_quotes[coord] = data

# Prepare data for HTML component
matrix_data = {
    "column_names": column_names,
    "row_names": row_names,
    "definitions": definitions,
    "cell_quotes": filtered_quotes,
    "highlighted_cells": highlighted_cells,
}

# HTML/JavaScript component
html = f'''
<!DOCTYPE html>
<html>
<head>
    <style>
        .matrix-wrapper {{ overflow: auto; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #f8f9fa; position: sticky; top: 0; }}
        .highlighted {{ border: 2px solid #2196f3 !important; cursor: pointer; }}
        
        /* Modal styles */
        .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.4); }}
        .modal-content {{ background-color: #fefefe; margin: 15% auto; padding: 20px; border: 1px solid #888; width: 80%; max-width: 600px; position: relative; }}
        .close {{ color: #aaa; float: right; font-size: 28px; font-weight: bold; }}
        .close:hover, .close:focus {{ color: black; text-decoration: none; cursor: pointer; }}
        #modalQuotes p {{ margin: 10px 0; padding: 5px; background: #f8f9fa; border-radius: 4px; }}
        .cell-content {{ display: flex; flex-direction: column; justify-content: center; align-items: center; }}
        .percentage {{ 
            font-weight: bold; 
            margin-bottom: 5px; 
            width: 100%;
            text-align: center;
            padding: 3px;
            border-radius: 4px;
        }}
        .explanation {{ font-size: 0.9em; color: #555; }}
    </style>
</head>
<body>
    <div class="matrix-wrapper">
        <table id="matrixTable"></table>
    </div>
    <div id="quoteModal" class="modal">
        <div class="modal-content">
            <span class="close">&times;</span>
            <div id="modalQuotes"></div>
        </div>
    </div>
    <script>
        const data = {json.dumps(matrix_data, ensure_ascii=False)};
        
        function calculateColor(percentage) {{
            // Excel-style gradient from green (0%) to red (100%)
            const hue = 120 - (percentage * 1.2); // 120° (green) to 0° (red)
            return `hsl(${{hue}}deg, 100%, 50%)`;
        }}

        function buildMatrix() {{
            const table = document.getElementById('matrixTable');
            table.innerHTML = '';
            
            // Build header
            let headerRow = '<tr><th>Factors</th>';
            data.column_names.forEach(col => headerRow += `<th>${{col}}</th>`);
            headerRow += '</tr>';
            table.innerHTML = headerRow;
            
            // Build rows
            data.row_names.forEach((rowName, rowIndex) => {{
                let rowHtml = `<tr><td>${{rowName}}</td>`;
                data.column_names.forEach((colName, colIndex) => {{
                    const coord = `${{rowIndex}},${{colIndex}}`;
                    const content = data.definitions[rowName][colName];
                    const [percentage, explanation] = content.split('|');
                    const percentValue = parseFloat(percentage) || 0;
                    const isHighlighted = data.highlighted_cells.includes(coord);
                    const quotes = data.cell_quotes[coord]?.quotes || [];
                    
                    // Calculate color
                    const color = calculateColor(percentValue);
                    
                    rowHtml += `
                        <td class="${{isHighlighted ? 'highlighted' : ''}}" data-quotes='${{JSON.stringify(quotes)}}'>
                            <div class="cell-content">
                                <div class="percentage" style="background: ${{color}}">
                                    ${{isHighlighted ? `${{percentage}}%` : ''}}
                                </div>
                                <div class="explanation">${{explanation}}</div>
                            </div>
                        </td>`;
                }});
                rowHtml += '</tr>';
                table.innerHTML += rowHtml;
            }});
        }}
        
        buildMatrix();
        
        // Modal handling
        const modal = document.getElementById('quoteModal');
        const modalQuotes = document.getElementById('modalQuotes');
        const closeSpan = document.getElementsByClassName('close')[0];
        
        document.getElementById('matrixTable').addEventListener('click', function(event) {{
            const cell = event.target.closest('td.highlighted');
            if (cell) {{
                const quotes = JSON.parse(cell.getAttribute('data-quotes'));
                if (quotes?.length) {{
                    modalQuotes.innerHTML = quotes.map(quote => `<p>${{quote}}</p>`).join('');
                    modal.style.display = 'block';
                }}
            }}
        }});
        
        closeSpan.onclick = () => modal.style.display = 'none';
        window.onclick = (event) => {{ if (event.target === modal) modal.style.display = 'none'; }};
    </script>
</body>
</html>'''

if st.session_state.applied_filters:
    st.info("ℹ️ Please click on the highlighted cells to view the corresponding quotes")

st.components.v1.html(html, height=800, scrolling=True)
