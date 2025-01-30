pip install streamlit-aggrid
import streamlit as st
import pandas as pd

# Configure app
st.set_page_config(page_title="Flexibility Contributing Factors Heatmap Matrix", layout="wide")

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("matrix explained.xlsx", index_col=0)
        df.index = df.index.str.strip()
        df.columns = ['Processes', 'Products', 'Tools']
        return df
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return pd.DataFrame()

df = load_data()

# Configuration
filters_data = {
    "Phases": ["Monitoring", "Pre-Contract", "Planning", "Execution", "Delivery"],
    "Roles": ["Consultant", "Engineer", "Manager"]
}

cell_quotes = {
    ("Pre-Contract Motivations", "Processes"): [
        "Chocolate", 
        "Yes we can make a dynamic heatmap matrix work :)"
    ],
    ("Leadership commitment to being flexible", "Products"): [
        "I think deepseek's R1 model is better for fixing code errors",
        "An americano with an extra shot"
    ]
}

# Create filters
col1, col2 = st.columns(2)
with col1:
    main_filter = st.selectbox("Main Filter", ["Select Filter"] + list(filters_data.keys()))
with col2:
    subfilter = st.selectbox("Subfilter", ["Select Subfilter"] + (filters_data.get(main_filter, []) if main_filter != "Select Filter" else []))

# Generate HTML table
table_html = """
<style>
    .matrix-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
    }
    .matrix-table th, .matrix-table td {
        border: 1px solid #ddd;
        padding: 12px;
        text-align: left;
    }
    .matrix-table th {
        background-color: #1a73e8;
        color: white;
    }
    .highlighted {
        background-color: #e8f0fe;
        border: 2px solid #1a73e8 !important;
    }
</style>

<table class='matrix-table'>
    <tr>
        <th>Factors</th>
        <th>Processes</th>
        <th>Products</th>
        <th>Tools</th>
    </tr>
"""

for idx, row in enumerate(df.index):
    table_html += f"""
    <tr>
        <td><strong>{row}</strong></td>
        <td{' class="highlighted"' if (row, 'Processes') in cell_quotes else ''}>{df.loc[row, 'Processes']}</td>
        <td{' class="highlighted"' if (row, 'Products') in cell_quotes else ''}>{df.loc[row, 'Products']}</td>
        <td{' class="highlighted"' if (row, 'Tools') in cell_quotes else ''}>{df.loc[row, 'Tools']}</td>
    </tr>
    """

table_html += "</table>"

# Display the matrix
st.markdown(table_html, unsafe_allow_html=True)

# Add tooltips
st.markdown("""
<script>
// Simple hover tooltip implementation
document.querySelectorAll('.highlighted').forEach(cell => {
    cell.addEventListener('mouseover', function(e) {
        this.style.cursor = 'pointer';
        this.title = "Quotes:\\n- " + %s;
    });
});
</script>
""" % str(list(cell_quotes.values())).replace("'", ""), unsafe_allow_html=True)
