import streamlit as st
import pandas as pd
import json

# Set page config
st.set_page_config(layout="wide")

@st.cache_data
def load_matrix_data():
    try:
        # Load definitions from Excel
        df = pd.read_excel("matrix explained.xlsx", index_col=0)
        df.index = df.index.str.strip()
        df.columns = ['Processes', 'Products', 'Tools']
        return df
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        st.stop()

# Load definitions from Excel
df_definitions = load_matrix_data()
row_names = df_definitions.index.tolist()
column_names = df_definitions.columns.tolist()

# Configure percentages (from your provided data)
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
    'Slack': {'Processes': 11, 'Products': 9, 'Tools': 5},
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
    "0,0": {"quotes": ["We can change the design...", "Yes we can..."], "filters": {"Roles": ["Consultant"]}},
    # ... (keep your original quotes)
}

# Streamlit UI
st.title("Flexibility Contributing Factors Matrix")

# Filter selection (keep your original filter code)
# ... [Your existing filter code] ...

# Prepare matrix data
matrix_data = {
    "column_names": column_names,
    "row_names": row_names,
    "definitions": df_definitions.to_dict(),
    "percentages": percentages,
    "cell_quotes": cell_quotes,
    "highlighted_cells": highlighted_cells
}

# HTML/JavaScript component
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
            if (value >= 50) return '#8b0000';
            if (value >= 40) return '#ff0000';
            if (value >= 30) return '#ff4500';
            if (value >= 20) return '#ffa500';
            if (value >= 10) return '#ffd700';
            return '#008000';
        }}

        function buildMatrix() {{
            const table = document.getElementById('matrixTable');
            table.innerHTML = '';
            
            // Create header
            let headerRow = '<tr><th>Factors</th>';
            data.column_names.forEach(col => {{ headerRow += `<th>${{col}}</th>`; }});
            headerRow += '</tr>';
            table.innerHTML = headerRow;

            // Create rows
            data.row_names.forEach((rowName, rowIndex) => {{
                let rowHtml = `<tr><td><strong>${{rowName}}</strong></td>`;
                data.column_names.forEach((colName, colIndex) => {{
                    const value = data.percentages[rowName][colName];
                    const definition = data.definitions[colName][rowName];
                    const color = getColor(value);
                    const coord = `${{rowIndex}},${{colIndex}}`;
                    const isHighlighted = data.highlighted_cells.includes(coord);
                    
                    rowHtml += `
                        <td class="${{isHighlighted ? 'highlighted' : ''}} heatmap-cell" 
                            data-quotes='${{JSON.stringify(data.cell_quotes[coord]?.quotes || [])}}'>
                            <div class="color-overlay" style="background-color: ${{color}}"></div>
                            <div class="percentage">${{value}}%</div>
                            <div class="definition">${{definition}}</div>
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

# Render the component
st.components.v1.html(html, height=800, scrolling=True)
