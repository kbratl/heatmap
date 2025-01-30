# Update the HTML styling section with these changes:
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
            max-width: 100vw;  /* Add viewport constraint */
        }}
        table {{
            border-collapse: collapse;
            min-width: {300 + 200 * len(column_names)}px;  /* Dynamic width calculation */
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
            width: 200px;  /* Fixed column width */
            min-width: 200px;  /* Prevent column shrinking */
            max-width: 200px;  /* Prevent column expanding */
            white-space: normal;  /* Allow text wrapping */
        }}
        th:first-child, td:first-child {{
            width: 300px;
            min-width: 300px;
            position: sticky;
            left: 0;
            z-index: 2;
            background: #f8f9fa;
        }}
        th {{
            position: sticky;
            top: 0;
            background: #f8f9fa;
            z-index: 3;
        }}
        tr:nth-child(even) td {{
            background-color: #f9f9f9;
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
