import streamlit as st
import pandas as pd
import json

# Set page config
st.set_page_config(layout="wide")

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

# Matrix configuration
row_names = [
    "Pre-Contract Motivations", "Post-Contract Motivations", "Questioning Competence",
    "Modeling and Comparing Competence", "Interpretation Competence",
    "Degree of Control in Management Practices", "Leadership Commitment to Being Flexible",
    "Experimentation and Learning", "Defining Flexibility Related Project Objectives",
    "Long-term Perspective", "Buffers", "Slack", "Supplier-Buyer Cooperation",
    "Multidisciplinary Coordination", "Flexibility as Threat vs Opportunity",
    "Immediate Profit vs Sustained Success"
]
column_names = ['Processes', 'Products', 'Tools']

# Prepare data for HTML component
matrix_data = {
    "column_names": column_names,
    "row_names": row_names,
    "highlighted_cells": highlighted_cells,
    "cell_quotes": cell_quotes
}

# HTML/JavaScript component with heatmap
html = f'''
<!DOCTYPE html>
<html>
<head>
    <style>
        .matrix-wrapper {{ overflow: auto; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
        th {{ background: #f8f9fa; position: sticky; top: 0; }}
        .highlighted {{ border: 2px solid #2196f3 !important; cursor: pointer; }}
        
        /* Heatmap styling */
        .heatmap-cell {{ 
            font-weight: bold;
            color: black;
            position: relative;
            min-width: 100px;
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
        .percentage {{
            position: relative;
            z-index: 2;
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
            // Red (high) to Green (low) scale
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
            
            // Create header
            let headerRow = '<tr><th>Factors</th>';
            data.column_names.forEach(col => {{ headerRow += `<th>${{col}}</th>`; }});
            headerRow += '</tr>';
            table.innerHTML = headerRow;

            // Percentage data
            const percentages = {{
                "Pre-Contract Motivations": {{"Processes": 16, "Products": 8, "Tools": 13}},
                "Post-Contract Motivations": {{"Processes": 50, "Products": 11, "Tools": 6}},
                "Questioning Competence": {{"Processes": 23, "Products": 13, "Tools": 6}},
                "Modeling and Comparing Competence": {{"Processes": 25, "Products": 6, "Tools": 27}},
                "Interpretation Competence": {{"Processes": 27, "Products": 9, "Tools": 8}},
                "Degree of Control in Management Practices": {{"Processes": 33, "Products": 8, "Tools": 9}},
                "Leadership Commitment to Being Flexible": {{"Processes": 42, "Products": 13, "Tools": 13}},
                "Experimentation and Learning": {{"Processes": 9, "Products": 14, "Tools": 13}},
                "Defining Flexibility Related Project Objectives": {{"Processes": 19, "Products": 8, "Tools": 8}},
                "Long-term Perspective": {{"Processes": 13, "Products": 11, "Tools": 9}},
                "Buffers": {{"Processes": 25, "Products": 5, "Tools": 6}},
                "Slack": {{"Processes": 11, "Products": 9, "Tools": 5}},
                "Supplier-Buyer Cooperation": {{"Processes": 25, "Products": 19, "Tools": 13}},
                "Multidisciplinary Coordination": {{"Processes": 55, "Products": 11, "Tools": 20}},
                "Flexibility as Threat vs Opportunity": {{"Processes": 25, "Products": 11, "Tools": 11}},
                "Immediate Profit vs Sustained Success": {{"Processes": 20, "Products": 14, "Tools": 5}}
            }};

            // Create rows
            data.row_names.forEach(rowName => {{
                let rowHtml = `<tr><td><strong>${{rowName}}</strong></td>`;
                data.column_names.forEach(colName => {{
                    const value = percentages[rowName][colName];
                    const color = getColor(value);
                    const rowIndex = data.row_names.indexOf(rowName);
                    const colIndex = data.column_names.indexOf(colName);
                    const coord = `${{rowIndex}},${{colIndex}}`;
                    const isHighlighted = data.highlighted_cells.includes(coord);
                    
                    rowHtml += `
                        <td class="${{isHighlighted ? 'highlighted' : ''}} heatmap-cell" 
                            data-quotes='${{JSON.stringify(data.cell_quotes[coord]?.quotes || [])}}'>
                            <div class="color-overlay" style="background-color: ${{color}}"></div>
                            <div class="percentage">${{value}}%</div>
                        </td>`;
                }});
                rowHtml += '</tr>';
                table.innerHTML += rowHtml;
            }});
        }}

        // Modal handling
        const modal = document.getElementById('quoteModal');
        const modalQuotes = document.getElementById('modalQuotes');
        const closeSpan = document.getElementsByClassName('close')[0];
        
        document.getElementById('matrixTable').addEventListener('click', function(event) {{
            const target = event.target.closest('td');
            if (target && target.classList.contains('highlighted')) {{
                const quotes = JSON.parse(target.getAttribute('data-quotes'));
                if (quotes && quotes.length > 0) {{
                    modalQuotes.innerHTML = quotes.map(quote => `<p>${{quote}}</p>`).join('');
                    modal.style.display = 'block';
                }}
            }}
        }});
        
        closeSpan.onclick = function() {{ modal.style.display = 'none'; }};
        window.onclick = function(event) {{ if (event.target === modal) modal.style.display = 'none'; }};

        buildMatrix();
    </script>
</body>
</html>
'''

# Show disclaimer
if st.session_state.applied_filters:
    st.info("ℹ️ Please click on the highlighted cells to view the corresponding quotes")

# Definitions section
st.subheader("Definitions")
definitions = """
**Pre-Contract Motivations**: [Add your definition here]
**Post-Contract Motivations**: [Add your definition here]
**Questioning Competence**: [Add your definition here]
**Modeling and Comparing Competence**: [Add your definition here]
**Interpretation Competence**: [Add your definition here]
**Degree of Control in Management Practices**: [Add your definition here]
**Leadership Commitment to Being Flexible**: [Add your definition here]
**Experimentation and Learning**: [Add your definition here]
**Defining Flexibility Related Project Objectives**: [Add your definition here]
**Long-term Perspective**: [Add your definition here]
**Buffers**: [Add your definition here]
**Slack**: [Add your definition here]
**Supplier-Buyer Cooperation**: [Add your definition here]
**Multidisciplinary Coordination**: [Add your definition here]
**Flexibility as Threat vs Opportunity**: [Add your definition here]
**Immediate Profit vs Sustained Success**: [Add your definition here]
"""
st.markdown(definitions)

# Render the component
st.components.v1.html(html, height=800, scrolling=True)
