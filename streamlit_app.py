html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 0;
            height: 100%;
        }}
        .matrix-container {{
            overflow: auto;
            height: 100vh;
            padding: 20px;
        }}
        table {{
            border-collapse: collapse;
            min-width: 800px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
            min-width: 200px;
            position: sticky;
            left: 0;
            background: white;
            z-index: 1;
        }}
        th:first-child, td:first-child {{
            min-width: 300px;
            left: 0;
            z-index: 2;
            background: #f8f9fa;
            position: sticky;
            left: 0;
        }}
        th {{
            background: #f8f9fa;
            position: sticky;
            top: 0;
            z-index: 3;
        }}
        .dimmed {{ 
            background: #f8f9fa; 
            color: #999; 
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
    <div class="matrix-container">
        <table id="matrixTable"></table>
    </div>

    <!-- Keep the existing JavaScript -->
</body>
</html>
"""

# This is the corrected components call:
st.components.v1.html(html, height=1200)

