import re

file_path = r'd:\sodimac\2026\databases\backup.sql'
table_name = 'items_licitacion'

try:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        match = re.search(f'CREATE TABLE public.{table_name} \((.*?)\);', content, re.DOTALL)
        if not match:
            table_name = 'items_licitados'
            match = re.search(f'CREATE TABLE public.{table_name} \((.*?)\);', content, re.DOTALL)
        
        if match:
            body = match.group(1)
            columns = []
            for line in body.split(','):
                parts = line.strip().split()
                if parts:
                    columns.append(line.strip())
            with open('columns.txt', 'w') as out:
                out.write(f"Table: {table_name}\n")
                out.write("\n".join(columns))
            print("Done")
        else:
            print("Table not found")
except Exception as e:
    print(f"Error: {e}")
