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
    "Organisation Types": ["Contractor", "Client", "Consultant"],
    "Roles": ["Analyst", "Architect", "Consultant", "Director", 
             "Engineer", "Manager", "President", "Vice President"],
}

# Configure cell quotes
cell_quotes = {
    "0,0": {"quotes": ["Chocolate", "Yes we can make a dynamic heatmap matrix work :)"], "filters": {"Roles": ["Consultant"]}},
    "7,1": {"quotes": ["I do not know if there is a word limit", "An americano with an extra shot""], "filters": {"Roles": ["Consultant"]}},
    "6,1": {"quotes": ["I think deepseek R1 model is better for fixing code errors", "An americano with an extra shot"], "filters": {"Roles": ["Consultant"]}},
    "9,2": {"quotes": ["Will we display all the quotes", "We might change the design this is just a prototype..."], "filters": {"Roles": ["Consultant"]}},
    "4,1": {"quotes": ["Leadership should drive flexibility initiatives", "Regular review meetings with product teams"], "filters": {"Roles": ["Consultant"]}},
    "8,2": {"quotes": ["Long-term planning supports better tool integration", "Tools should evolve with project needs"], "filters": {"Roles": ["Consultant"]}},
}

# Streamlit UI
st.title("Flexibility Matrix Explorer")

# Filter selection
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    main_filter = st.selectbox("Select Main Filter", [""] + list(filters_data.keys()), key="main_filter")
with col2:
    subfilter_options = [""] + filters_data.get(main_filter, []) if main_filter else [""]
    subfilter = st.selectbox("Select Subfilter", subfilter_options, key="subfilter")
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
        .highlighted {{ background: #e3f2fd !important; border: 2px solid #2196f3 !important; cursor: pointer; }}
        
        /* Modal styles */
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.4);
        }}
        .modal-content {{
            background-color: #fefefe;
            margin: 15% auto;
            padding: 20px;
            border: 1px solid #888;
            width: 80%;
            max-width: 600px;
            position: relative;
        }}
        .close {{
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
        }}
        .close:hover,
        .close:focus {{
            color: black;
            text-decoration: none;
            cursor: pointer;
        }}
        #modalQuotes p {{
            margin: 10px 0;
            padding: 5px;
            background: #f8f9fa;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="matrix-wrapper">
        <table id="matrixTable"></table>
    </div>
    <!-- Modal Structure -->
    <div id="quoteModal" class="modal">
        <div class="modal-content">
            <span class="close">&times;</span>
            <div id="modalQuotes"></div>
        </div>
    </div>
    <script>
        const data = {json.dumps(matrix_data, ensure_ascii=False)};
        function buildMatrix() {{
            const table = document.getElementById('matrixTable');
            table.innerHTML = '';
            let headerRow = '<tr><th>Factors</th>';
            data.column_names.forEach(col => {{ headerRow += `<th>${{col}}</th>`; }});
            headerRow += '</tr>';
            table.innerHTML = headerRow;
            data.row_names.forEach((rowName, rowIndex) => {{
                let rowHtml = `<tr><td>${{rowName}}</td>`;
                data.column_names.forEach((colName, colIndex) => {{
                    const coord = `${{rowIndex}},${{colIndex}}`;
                    const content = data.definitions[rowName][colName];
                    const isHighlighted = data.highlighted_cells.includes(coord);
                    const quotes = data.cell_quotes[coord]?.quotes || [];
                    rowHtml += `<td class="${{isHighlighted ? 'highlighted' : ''}}" data-quotes='${{JSON.stringify(quotes)}}'>${{content}}</td>`;
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
        
        // Click handler for cells
        document.getElementById('matrixTable').addEventListener('click', function(event) {{
            const target = event.target;
            if (target.tagName === 'TD' && target.classList.contains('highlighted')) {{
                const quotes = JSON.parse(target.getAttribute('data-quotes'));
                if (quotes && quotes.length > 0) {{
                    modalQuotes.innerHTML = quotes.map(quote => `<p>${{quote}}</p>`).join('');
                    modal.style.display = 'block';
                }}
            }}
        }});
        
        // Close modal handlers
        closeSpan.onclick = function() {{
            modal.style.display = 'none';
        }};
        window.onclick = function(event) {{
            if (event.target === modal) {{
                modal.style.display = 'none';
            }}
        }};
    </script>
</body>
</html>'''
# Show disclaimer only when filters are applied
if st.session_state.applied_filters:
    st.info("ℹ️ Click on the highlighted cells to view corresponding quotes")

# Render the component
st.components.v1.html(html, height=800, scrolling=True)
