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

# Configure filters and cell quotes (same as previous)

# Streamlit UI (same filter components as before)

# HTML/JavaScript component with full-space matrix
html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ 
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
        }}
        .matrix-wrapper {{
            width: 100%;
            height: 100vh;
            overflow: visible;
            position: relative;
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
            min-width: 200px;
            max-width: 300px;
            white-space: normal;
            background: white;
            position: relative;
        }}
        th:first-child {{
            position: sticky;
            left: 0;
            z-index: 3;
            background: #f8f9fa;
            min-width: 250px;
        }}
        td:first-child {{
            position: sticky;
            left: 0;
            z-index: 2;
            background: #f8f9fa;
        }}
        th {{
            position: sticky;
            top: 0;
            z-index: 3;
            background: #f8f9fa;
        }}
        .matrix-container {{
            width: 100%;
            overflow: visible;
            position: relative;
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
            max-width: 300px;
            z-index: 1000;
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
                            ${{content}}
                        </td>
                    `;
                }});
                rowHtml += '</tr>';
                table.innerHTML += rowHtml;
            }});
            
            // Calculate required width
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

# Render the component with appropriate height
st.components.v1.html(html, height=1000)
