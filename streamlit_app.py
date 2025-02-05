import streamlit as st
import pandas as pd
import json

# Set page config MUST be the first Streamlit command
st.set_page_config(layout="wide")

# Load and prepare data
file_path = "matrix explained.xlsx"
try:
    original_df = pd.read_excel(file_path, index_col=0)
    original_df.index = original_df.index.str.strip()
    original_df.columns = ['Processes', 'Products', 'Tools']
    row_names = original_df.index.tolist()
    column_names = original_df.columns.tolist()
    original_explanations = original_df.to_dict('index')
except Exception as e:
    st.error(f"Error loading Excel file: {e}")
    st.stop()

# Initialize default percentages
default_percentages = {
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

 # Dynamic percentages for filter combinations
dynamic_percentages = {
    ('Roles', 'Consultant'): {
        'Pre-Contract Motivations': {'Processes': 32},
        'Interpretation Competence': {'Products': 5},
        'Leadership commitment to being flexible': {'Products': 10},
        'Experimentation and learning': {'Products': 12},
        'Defining Flexibility Related Project Objectives': {'Tools': 25},
        'Long-term Perspective': {'Tools': 16},
    },
}       

# Initialize current percentages
current_percentages = {row: cols.copy() for row, cols in default_percentages.items()}

# Create INITIAL df
df = pd.DataFrame(index=row_names, columns=column_names)
for row in row_names:
    for col in column_names:
        explanation = original_explanations.get(row, {}).get(col, '')
        percent = current_percentages.get(row, {}).get(col, 0)
        df.at[row, col] = f"{percent}%|{explanation}"

# build definitions
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
    apply_pressed = st.button("Apply Filters")

# Session state management
if 'applied_filters' not in st.session_state:
    st.session_state.applied_filters = None

# Handle filter application
if apply_pressed:
    if main_filter and subfilter:
        st.session_state.applied_filters = (main_filter, subfilter)
    else:
        st.warning("Please select both a main filter and subfilter")
        st.session_state.applied_filters = None

# Process filters
filtered_quotes = {}
highlighted_cells = []

if st.session_state.applied_filters:
    main_filter, subfilter = st.session_state.applied_filters
    key = (main_filter, subfilter)
    
    # Update percentages
    if key in dynamic_percentages:
        for row, cols in dynamic_percentages[key].items():
            if row in current_percentages:
                current_percentages[row].update(cols)
    
    # Filter quotes
    for coord, data in cell_quotes.items():
        if main_filter in data["filters"] and subfilter in data["filters"][main_filter]:
            highlighted_cells.append(coord)
            filtered_quotes[coord] = data["quotes"]

# Rebuild DataFrame with current data
df = pd.DataFrame(index=row_names, columns=column_names)
for row in row_names:
    for col in column_names:
        explanation = original_explanations.get(row, {}).get(col, '')
        percent = current_percentages.get(row, {}).get(col, 0)
        
        # Show percentage if: no filters applied OR cell is highlighted
        show_percentage = not st.session_state.applied_filters or \
                        f"{row_names.index(row)},{column_names.index(col)}" in highlighted_cells
        
        if show_percentage:
            df.at[row, col] = f"{percent}|{explanation}"
        else:
            df.at[row, col] = f"|{explanation}"

# Rebuild definitions
definitions = {
    row: {col: str(df.at[row, col]) for col in column_names}
    for row in row_names
}

# Prepare matrix data
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
        .highlighted {{ background: #e3f2fd !important; border: 2px solid #2196f3 !important; cursor: pointer; }}
        .cell-content {{ display: flex; flex-direction: column; justify-content: center; align-items: center; }}
        .percentage {{
            font-weight: bold;
            margin-bottom: 2mm;
            padding: 2px;
            width: 100%;
            text-align: center;
            border-radius: 3px;
            color: white;
        }}
        .explanation {{ font-size: 0.9em; color: #555; }}
        /* Modal Styles */
        .modal {{
            display: none;
            position: fixed;
            z-index: 1;
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
        function getHeatmapColor(percentage) {{
            let hue, lightness;
            if (percentage <= 50) {{
                // Green (120) to Yellow (60) for low to medium values
                hue = 120 - (percentage * 1.2);
            }} else {{
                // Yellow (60) to Red (0) for medium to high values
                hue = 60 - ((percentage - 50) * 2.4);
            }}
            
            lightness = 85 - (percentage * 0.75);  // Higher percentage = Darker
            // Ensure higher saturation for deeper reds
            saturation = 95 - (percentage * 0.3); 
            
            return "hsl(" + hue + saturation + lightness + "%)";
        }}
        function buildMatrix() {{
            const table = document.getElementById('matrixTable');
            table.innerHTML = '';
            
            // Build headers
            let headerRow = '<tr><th>Factors</th>';
            data.column_names.forEach(col => headerRow += `<th>${{col}}</th>`);
            headerRow += '</tr>';
            table.innerHTML = headerRow;
            
            // Build body
            data.row_names.forEach((rowName, rowIndex) => {{
                let rowHtml = `<tr><td>${{rowName}}</td>`;
                data.column_names.forEach((colName, colIndex) => {{
                    const coord = `${{rowIndex}},${{colIndex}}`;
                    const content = data.definitions[rowName][colName];
                    const [percentage, explanation] = content.split('|');
                    const isHighlighted = data.highlighted_cells.includes(coord);
                    
                    const hasPercentage = percentage !== '';
                    const percentValue = hasPercentage ? parseFloat(percentage) : null;
                    
                    let percentageDisplay = '';
                    if (hasPercentage) {{
                        const color = getHeatmapColor(percentValue);
                        percentageDisplay = `
                            <div class="percentage" style="background-color: ${{color}}">
                                ${{percentValue}}%
                            </div>`;
                    }}
                    
                    const quotes = data.cell_quotes[coord] || [];
                    
                    rowHtml += `
                        <td class="${{isHighlighted ? 'highlighted' : ''}}" 
                            data-quotes='${{JSON.stringify(quotes)}}'>
                            <div class="cell-content">
                                ${{percentageDisplay}}
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
                if (quotes && quotes.length > 0) {{
                    modalQuotes.innerHTML = quotes.map(quote => `<p>${{quote}}</p>`).join('');
                    modal.style.display = 'block';
                }}
            }}
        }});
        
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
</html>
'''

if st.session_state.applied_filters:
    st.info("ℹ️ Please click on the highlighted cells to view the corresponding quotes")
    
# Render the component
st.components.v1.html(html, height=800, scrolling=True)
