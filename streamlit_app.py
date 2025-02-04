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

# Add percentages data (from your provided values)
percentages = {
    'Pre-Contract Motivations': {'Processes': 16, 'Products': 8, 'Tools': 13},
    'Post-Contract Motivations': {'Processes': 50, 'Products': 11, 'Tools': 6},
    'Questioning Competence': {'Processes': 23, 'Products': 13, 'Tools': 6},
    'Modeling and Comparing Competence': {'Processes': 25, 'Products': 6, 'Tools': 27},
    'Interpretation Competence': {'Processes': 27, 'Products': 9, 'Tools': 8},
    'Degree of Control in Management Practices': {'Processes': 33, 'Products': 8, 'Tools': 9},
    'Leadership Commitment to Being Flexible': {'Processes': 42, 'Products': 13, 'Tools': 13},
    'Experimentation and Learning': {'Processes': 9, 'Products': 14, 'Tools': 13},
    'Defining Flexibility Related Project Objectives': {'Processes': 19, 'Products': 8, 'Tools': 8},
    'Long-term Perspective': {'Processes': 13, 'Products': 11, 'Tools': 9},
    'Buffers': {'Processes': 25, 'Products': 5, 'Tools': 6},
    'Slack': {'Processes': 11, 'Products': 9, 'Tools': 5},  # Updated Slack X Tools to 5%
    'Supplier-Buyer Cooperation': {'Processes': 25, 'Products': 19, 'Tools': 13},
    'Multidisciplinary Coordination': {'Processes': 55, 'Products': 11, 'Tools': 20},
    'Flexibility as Threat vs Opportunity': {'Processes': 25, 'Products': 11, 'Tools': 11},
    'Immediate Profit vs Sustained Success': {'Processes': 20, 'Products': 14, 'Tools': 5}
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
          /* Heatmap styles */
        .heatmap-cell {{
            position: relative;
            min-width: 120px;
            height: 80px;
        }}
        .percentage {{
            font-weight: bold;
            font-size: 1.2em;
            position: relative;
            z-index: 2;
        }}
        .definition {{
            font-size: 0.8em;
            color: #666;
            margin-top: 5px;
        }}
        .color-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0.3;
            z-index: 1;
        }}
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
         function getColor(value) {{
            // Excel-like color scale (red-high to green-low)
            if (value >= 50) return '#8b0000';  // Dark red
            if (value >= 40) return '#ff0000';  // Bright red
            if (value >= 30) return '#ff4500';  // Orange-red
            if (value >= 20) return '#ffa500';  // Orange
            if (value >= 10) return '#ffd700';  // Yellow
            return '#008000';  // Green
        }}

        function buildMatrix() {{
            const table = document.getElementById('matrixTable');
            table.innerHTML = '';
            let headerRow = '<tr><th>Factors</th>';
            data.column_names.forEach(col => {{ headerRow += `<th>${{col}}</th>`; }});
            headerRow += '</tr>';
            table.innerHTML = headerRow;
            
            rowHtml += `
                        <td class="${{isHighlighted ? 'highlighted' : ''}} heatmap-cell" 
                            data-quotes='${{JSON.stringify(quotes)}}'>
                            <div class="color-overlay" style="background-color: ${{color}}"></div>
                            <div class="percentage">${{percentage}}%</div>
                            <div class="definition">${{content}}</div>
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
    st.info("ℹ️ Please click on the highlighted cells to view the corresponding quotes")

# Render the component
st.components.v1.html(html, height=800, scrolling=True)
