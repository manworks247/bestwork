import json
import ast

with open('entity_resolution_project/google_colab/business_entity_resolution_colab.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")
errors = 0
for i, cell in enumerate(nb['cells']):
    cell_type = cell['cell_type']
    source = ''.join(cell['source'])
    title = source.split('\n')[0][:50]
    print(f"Cell {i+1} ({cell_type:8s}): {title}")
    if cell_type == 'code':
        # Remove shell lines like !pip install
        py_lines = [line for line in source.split('\n') if not line.strip().startswith('!')]
        py_code = '\n'.join(py_lines)
        try:
            ast.parse(py_code)
            print("  -> AST Syntax: VALID")
        except SyntaxError as e:
            print(f"  -> SYNTAX ERROR in cell {i+1}: {e}")
            errors += 1

if errors == 0:
    print("\nSUCCESS: All notebook code cells have ZERO syntax errors!")
else:
    print(f"\nFAILURE: Found {errors} syntax error(s)!")
