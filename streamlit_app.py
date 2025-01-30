import streamlit as st
import pandas as pd
from jinja2 import Template

# Configure page first
st.set_page_config(layout="wide")

# Custom CSS injection
st.markdown("""
<style>
    /* Main container */
    .main {
        max-width: 1200px;
        padding: 2rem;
    }
    
    /* Filters section */
    .filter-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Matrix table */
    .matrix-table {
        width: 100%;
        border-collapse: collapse;
        background: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    
    .matrix-table th {
        background: #2c3e50;
        color: white;
        padding: 1rem;
        text-align: left;
        position: sticky;
        top: 0;
    }
    
    .matrix-table td {
        padding: 1rem;
        border: 1px solid #dee2e6;
        vertical-align: top;
        min-width: 300px;
    }
    
    .matrix-table tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    
    /* Tooltip styling */
    .tooltip {
        visibility: hidden;
        position: absolute;
        background: #ffffff;
        border: 1px solid #dee2e6;
        padding: 1rem;
        border-radius: 4px;
        z-index: 1000;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        width: 300px;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
    }
    
    td:hover .tooltip {
        visibility: visible;
    }
    
    /* Highlighted cells */
    .highlighted {
        background: #e3f2fd !important;
        border: 2px solid #2196f3 !important;
        position: relative;
    }
</style>
""", unsafe_allow_html=True)

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

if not df.empty:
    st.title("Flexibility Matrix Explorer")
    
    with st.container():
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            selected_filter = st.selectbox("Main Filter", ["Roles", "Phases"])
        with col2:
            subfilter_options = {
                "Roles": ["Consultant", "Engineer", "Manager"],
                "Phases": ["Pre-Contract", "Execution"]
            }
            selected_subfilter = st.selectbox("Subfilter", subfilter_options[selected_filter])
        st.markdown('</div>', unsafe_allow_html=True)

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

    filtered_quotes = {}
    if selected_filter == "Roles" and selected_subfilter == "Consultant":
        filtered_quotes = cell_quotes

    html_template = """
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
                    <div style="font-size: 14px; color: #333;">
                        <b>Quotes:</b>
                        <ul style="margin-top: 8px;">
                            {% for quote in quotes[(row, col)] %}
                            <li style="margin-bottom: 4px;">{{ quote }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                </div>
                {% endif %}
            </td>
            {% endfor %}
        </tr>
        {% endfor %}
    </table>
    """

    rendered_html = Template(html_template).render(
        rows=df.index.tolist(),
        columns=df.columns.tolist(),
        data=df,
        quotes=filtered_quotes
    )

    st.markdown(rendered_html, unsafe_allow_html=True)
else:
    st.write("No data loaded - check your Excel file")
