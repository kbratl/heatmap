# ... (keep previous imports and data loading code) ...

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
    st.session_state.applied_filters = (main_filter, subfilter)
    
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

# ... (keep the matrix_data preparation and HTML template code the same) ...

# Update the JavaScript buildMatrix function to add dimmed class:
html = f"""
<!-- Keep previous HTML/CSS -->
<script>
    // ... (existing script code) ...
    
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
    
    // ... (rest of the script) ...
</script>
"""

# Render the component
st.components.v1.html(html, height=1200)
