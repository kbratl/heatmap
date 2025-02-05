import streamlit as st
import pandas as pd
import json

# Set page config MUST be the first Streamlit command
st.set_page_config(layout="wide")

# Load and prepare data
file_path = "matrix explained.xlsx"
try:
    df = pd.read_excel(file_path, index_col=0)
    df.index = df.index.str.strip()  # Remove any extra spaces from row names
    df.columns = ['Processes', 'Products', 'Tools']  # Rename columns
    row_names = df.index.tolist()  # Get row names as a list
    column_names = df.columns.tolist()  # Get column names as a list
except Exception as e:
    st.error(f"Error loading Excel file: {e}")
    st.stop()


# Add percentages to the DataFrame
base_percentages = {
    "Pre-Contract Motivations": {"Processes": 16, "Products": 8, "Tools": 13},
    "Post-contract motivations": {"Processes": 50, "Products": 11, "Tools": 6},
    "Questioning Competence": {"Processes": 23, "Products": 13, "Tools": 6},
    "Modeling and comparing competence": {"Processes": 25, "Products": 6, "Tools": 27},
    "Interpretation Competence": {"Processes": 27, "Products": 9, "Tools": 8},
    "Degree of Control in Management Practices": {"Processes": 33, "Products": 8, "Tools": 9},
    "Leadership commitment to being flexible": {"Processes": 42, "Products": 13, "Tools": 13},
    "Experimentation and learning": {"Processes": 9, "Products": 14, "Tools": 13},
    "Defining Flexibility Related Project Objectives": {"Processes": 19, "Products": 8, "Tools": 8},
    "Long-term Perspective": {"Processes": 13, "Products": 11, "Tools": 9},
    "Buffers": {"Processes": 25, "Products": 5, "Tools": 6},
    "Slacks": {"Processes": 11, "Products": 9, "Tools": 0},
    "Supplier-Buyer Cooperation": {"Processes": 25, "Products": 19, "Tools": 13},
    "Multidisciplinary Coordination": {"Processes": 55, "Products": 11, "Tools": 20},
    "Flexibility as Threat vs Opportunity": {"Processes": 25, "Products": 11, "Tools": 11},
    "Immediate Profit vs Sustained Success": {"Processes": 20, "Products": 14, "Tools": 5},
}

# Modified percentages for rolesxconsultant
dynamic_percentages = {
    "0,0": {"value": 32, "filters": {"Roles": ["Consultant"]}},
    "4,1": {"value": 5, "filters": {"Roles": ["Consultant"]}},
    "6,1": {"value": 10, "filters": {"Roles": ["Consultant"]}},
    "7,1": {"value": 12, "filters": {"Roles": ["Consultant"]}},
    "9,2": {"value": 25, "filters": {"Roles": ["Consultant"]}},
    "8,2": {"value": 16, "filters": {"Roles": ["Consultant"]}},
}

# Initialize DataFrame with base percentages
for row, cols in base_percentages.items():
    for col, percent in cols.items():
        df.at[row, col] = f"{percent}%|{df.at[row, col]}"

# Validate base percentages
missing_percentage_rows = [row for row in base_percentages.keys() if row not in row_names]
if missing_percentage_rows:
    st.error(f"Missing rows in Excel: {missing_percentage_rows}")
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
    "0,0": {"quotes": ["We can change the design this is just a prototype, we can make it way more aesthetically pleasing!", "Yes we can make a dynamic heatmap matrix work :)"], "filters": {"Roles": ["Consultant"]}},
    "7,1": {"quotes": ["I do not know if there is a word limit", "An americano with an extra shot"], "filters": {"Roles": ["Consultant"]}},
    "6,1": {"quotes": ["I think deepseek R1 model is better for fixing code errors", "An americano with an extra shot"], "filters": {"Roles": ["Consultant"]}},
    "9,2": {"quotes": ["Will we display all the quotes", "Chocolate"], "filters": {"Roles": ["Consultant"]}},
    "4,1": {"quotes": ["I tried only for this combination so far, but it is working!!", "Dueting with a streamer while working on the code made the process way more fun"], "filters": {"Roles": ["Consultant"]}},
    "8,2": {"quotes": ["Long-term planning supports better tool integration", "Just writing random things to see if they all display"], "filters": {"Roles": ["Consultant"]}},
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
    st.write("")  # Vertical spacing
    st.write("")
    apply_pressed = st.button("Apply Filters")

# Initialize session state
for row, cols in base_percentages.items():
    for col, percent in cols.items():
        df.at[row, col] = f"{percent}%|{df.at[row, col]}"

# Handle filter application
if apply_pressed:
    if main_filter and subfilter:
        st.session_state.applied_filters = (main_filter, subfilter)
    else:
        st.warning("Please select both a main filter and subfilter before applying")
        st.session_state.applied_filters = None

# Calculate highlighted cells based on applied filters
filtered_quotes = {}
highlighted_cells = []
if st.session_state.applied_filters:
    main_filter, subfilter = st.session_state.applied_filters
    
    for coord, data in cell_quotes.items():
        if main_filter in data["filters"] and subfilter in data["filters"][main_filter]:
            highlighted_cells.append(coord)
            filtered_quotes[coord] = data  # Store filtered quotes correctly

# Apply dynamic percentages after filter application
if st.session_state.applied_filters:
    main_filter, subfilter = st.session_state.applied_filters
    
    # Apply dynamic percentages
    for coord, data in dynamic_percentages.items():
        if main_filter in data["filters"] and subfilter in data["filters"][main_filter]:
            row_idx, col_idx = map(int, coord.split(','))
            row_name = row_names[row_idx]
            col_name = column_names[col_idx]
            current_content = df.at[row_name, col_name].split('|')
            df.at[row_name, col_name] = f"{data['value']}%|{current_content[1]}"

# Rebuild definitions with updated percentages
definitions = {
    row: {col: str(df.at[row, col]) for col in column_names}
    for row in row_names
}

# Prepare data for HTML component
matrix_data = {
    "column_names": column_names,
    "row_names": row_names,
    "definitions": definitions,
    "cell_quotes": filtered_quotes,  # Pass only relevant quotes
    "highlighted_cells": highlighted_cells,
}

# Modified JavaScript heatmap function
heatmap_js = """
function getHeatmapColor(percentage) {
    // Convert percentage to hue (0-120 degrees: red to green)
    const hue = (100 - Math.min(percentage, 100)) * 1.2;
    const saturation = 80;
    const lightness = 50 + (percentage / 100 * 20);
    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
}
"""
# HTML/JavaScript component
html = f'''
<!DOCTYPE html>
<html>
<head>
    <style>
        .matrix-wrapper { overflow: auto; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #f8f9fa; position: sticky; top: 0; }
        .highlighted { border: 2px solid #2196f3 !important; cursor: pointer; }
        
        /* Percentage styling */
       .percentage {{
            font-weight: bold;
            margin-bottom: 5px;
            padding: 3px;
            border-radius: 4px;
            width: fit-content;
            background: rgba(255, 255, 255, 0.3);
        }}
        .cell-content {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            min-height: 80px;
        }}
        /* Modern gradient heatmap colors */
        .heatmap-0 {{ background-color: #ffd6e7; }}
        .heatmap-1 {{ background-color: #ffbfd3; }}
        .heatmap-2 {{ background-color: #ffa8bf; }}
        .heatmap-3 {{ background-color: #ff91ab; }}
        .heatmap-4 {{ background-color: #ff7a97; }}
        .heatmap-5 {{ background-color: #ff6383; }}
        .heatmap-6 {{ background-color: #ff4c6f; }}
        .heatmap-7 {{ background-color: #ff355b; }}
        .heatmap-8 {{ background-color: #ff1e47; }}
        .heatmap-9 {{ background-color: #ff0733; }}

     
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
        .cell-content {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }}
        .percentage {{
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .explanation {{
            font-size: 0.9em;
            color: #555;
        }}
        .heatmap-low {{ background-color: #d9f7be; }}
        .heatmap-medium {{ background-color: #ffd591; }}
        .heatmap-high {{ background-color: #ffa39e; }}
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
      function getHeatmapColor(percentage) {{
            const pinkShades = [
                '#ffd6e7', '#ffbfd3', '#ffa8bf', '#ff91ab',
                '#ff7a97', '#ff6383', '#ff4c6f', '#ff355b',
                '#ff1e47', '#ff0733'
            ];
            return pinkShades[Math.min(Math.floor(percentage/10), 9)];
        }}
    </script>

    <div class="matrix-wrapper">
        <table id="matrixTable"></table>
    </div>

   <!-- Single modal structure -->
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
            
            // Header row
           let headerRow = '<tr><th>Factors</th>';
            data.column_names.forEach(col => headerRow += `<th>${{col}}</th>`);
            table.innerHTML = headerRow + '</tr>';

            // Build rows
            data.row_names.forEach((rowName, rowIndex) => {{
                let rowHtml = `<tr><td>${{rowName}}</td>`;
                data.column_names.forEach((colName, colIndex) => {{
                    const coord = `${{rowIndex}},${{colIndex}}`;
                    const [percentage, explanation] = data.definitions[rowName][colName].split('|');
                    const color = getHeatmapColor(parseFloat(percentage));
                    
                    rowHtml += `
                        <td class="${{data.highlighted_cells.includes(coord) ? 'highlighted' : ''}}"
                            style="background-color: ${{color}}"
                            data-quotes='${{JSON.stringify(data.cell_quotes[coord]?.quotes || [])}}'>
                            <div class="cell-content">
                                <div class="percentage">${{percentage}}</div>
                                <div class="explanation">${{explanation}}</div>
                            </div>
                        </td>`;
                }});
                table.innerHTML += rowHtml + '</tr>';
            }});
        }}

       // Initialize matrix and modal handlers
        buildMatrix();
        const modal = document.getElementById('quoteModal');
        const modalQuotes = document.getElementById('modalQuotes');
        const closeSpan = document.getElementsByClassName('close')[0];

        document.getElementById('matrixTable').addEventListener('click', function(event) {{
            const cell = event.target.closest('td.highlighted');
            if (cell) {{
                const quotes = JSON.parse(cell.getAttribute('data-quotes'));
                if (quotes && quotes.length) {{
                    modalQuotes.innerHTML = quotes.map(quote => 
                        `<p>${{quote}}</p>`
                    ).join('');
                    modal.style.display = 'block';
                }}
            }}
        }});

       closeSpan.onclick = () => modal.style.display = 'none';
        window.onclick = (event) => {{
            if (event.target === modal) modal.style.display = 'none';
        }};
    </script>
</body>
</html>
'''

# Show disclaimer only when filters are applied
if st.session_state.applied_filters:
    st.info("ℹ️ Please click on the highlighted cells to view the corresponding quotes")

# Render the component
st.components.v1.html(html, height=800, scrolling=True)
