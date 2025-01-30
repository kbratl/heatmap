import streamlit as st
import pandas as pd

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
    "Roles": ["Analyst", "Architect", "Consultant", "Director", "Engineer", "Manager", "President", "Vice President"],
}

# Configure cell quotes with proper coordinates
cell_quotes = {
    "0,0": {  # Pre-Contract Motivations x Processes
        "quotes": ["Chocolate", "Yes we can make a dynamic heatmap matrix work :)"],
        "filters": {"Roles": ["Consultant"]}
    },
    "6,1": {  # Leadership commitment x Products (row 6, column 1)
        "quotes": ["I think deepseek's R1 model is better for fixing code errors", 
                 "An americano with an extra shot"],
        "filters": {"Roles": ["Consultant"]}
    },
    "9,2": {  # Long-term perspective x Tools (row 9, column 2)
        "quotes": ["Will we display all the quotes", 
                 "We might change the design this is just a prototype, we can make it more aesthetically pleasing and colorful!"],
        "filters": {"Roles": ["Consultant"]}
    }
}

# Streamlit UI
st.title("Flexibility Matrix Explorer")

# Filters
main_filter = st.selectbox("Select Main Filter", [""] + list(filters_data.keys()))
subfilter_options = filters_data.get(main_filter, [])
subfilter = st.selectbox("Select Subfilter", [""] + subfilter_options)

# Apply Filters
if st.button("Apply Filters"):
    highlighted = []
    for coord, data in cell_quotes.items():
        if main_filter in data.get("filters", {}):
            if subfilter in data["filters"][main_filter]:
                highlighted.append(coord)
    
    # Display the matrix
    st.write("### Matrix")
    for row_idx, row_name in enumerate(row_names):
        cols = st.columns(len(column_names) + 1)
        cols[0].write(row_name)
        for col_idx, col_name in enumerate(column_names):
            cell_key = f"{row_idx},{col_idx}"
            cell_value = definitions[row_name][col_name]
            if cell_key in highlighted:
                cols[col_idx + 1].markdown(f"**{cell_value}**", unsafe_allow_html=True)
            else:
                cols[col_idx + 1].write(cell_value)

# Display quotes on hover
st.write("### Hover over cells to see quotes")
for row_idx, row_name in enumerate(row_names):
    for col_idx, col_name in enumerate(column_names):
        cell_key = f"{row_idx},{col_idx}"
        quotes = cell_quotes.get(cell_key, {}).get("quotes", [])
        if quotes:
            st.write(f"**{row_name} - {col_name}**")
            for quote in quotes:
                st.write(f"- {quote}")
