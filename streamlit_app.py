import streamlit as st
import pandas as pd
from jinja2 import Template

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel("matrix explained.xlsx", index_col=0)
    df.index = df.index.str.strip()
    df.columns = ['Processes', 'Products', 'Tools']
    return df

df = load_data()
row_names = df.index.tolist()
column_names = df.columns.tolist()

# Configure filters and quotes
filters_data = {
    "Roles": ["Consultant", "Engineer", "Manager"],
    "Phases": ["Pre-Contract", "Execution"]
}

cell_quotes = {
    ("Pre-Contract Motivations", "Processes"): [
        "Chocolate", 
        "Yes we can make a dynamic matrix work :)"
    ],
    ("Leadership commitment to being flexible", "Products"): [
        "I think deepseek's R1 model is better for fixing code errors",
        "An americano with an extra shot"
    ]
}

# Create filters
selected_filter = st.selectbox("Main Filter", list(filters_data.keys()))
selected_subfilter = st.selectbox("Subfilter", filters_data[selected_filter])

# Generate matrix display
html_template = """
<style>
    .matrix-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 20px;
    }
    .matrix-table td, .matrix-table th {
        border: 1px solid #ddd;
        padding: 12px;
        position: relative;
    }
    .highlighted {
        background-color: #e3f2fd;
        border: 2px solid #2196f3 !important;
    }
    .tooltip {
        visibility: hidden;
        position: absolute;
        background: #fff;
        border: 1px solid #ddd;
        padding: 10px;
        border-radius: 4px;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
    }
    td:hover .tooltip {
        visibility: visible;
    }
</style>

<table class="matrix-table">
    <tr>
        <th>Factors</th>
        {% for col in columns %}
        <th>{{ col }}</th>
        {% endfor %}
    </tr>
    {% for row in rows %}
    <tr>
        <td><strong>{{ row }}</strong></td>
        {% for col in columns %}
        <td {% if (row, col) in quotes %}class="highlighted"{% endif %}>
            {{ data.loc[row, col] }}
            {% if (row, col) in quotes %}
            <div class="tooltip">
                <ul>
                    {% for quote in quotes[(row, col)] %}
                    <li>{{ quote }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endif %}
        </td>
        {% endfor %}
    </tr>
    {% endfor %}
</table>
"""

# Filter logic
filtered_quotes = {
    k: v for k, v in cell_quotes.items() 
    if (selected_filter == "Roles" and selected_subfilter == "Consultant")
}

# Render matrix
rendered_html = Template(html_template).render(
    rows=row_names,
    columns=column_names,
    data=df,
    quotes=filtered_quotes
)

st.markdown(rendered_html, unsafe_allow_html=True)
