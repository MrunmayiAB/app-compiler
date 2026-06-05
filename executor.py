import json

def generate_sql(db_schema: dict) -> str:
    """Takes the db_schema from Stage 3 and generates real SQL CREATE TABLE statements."""
    
    sql_lines = []
    sql_lines.append("-- Auto-generated SQL from App Compiler")
    sql_lines.append("-- This file can be run directly on any SQL database\n")
    
    type_map = {
        "INTEGER": "INTEGER",
        "VARCHAR": "VARCHAR(255)",
        "TEXT": "TEXT",
        "BOOLEAN": "BOOLEAN",
        "DATETIME": "DATETIME",
        "FLOAT": "FLOAT"
    }
    
    tables = db_schema.get("tables", [])
    
    for table in tables:
        table_name = table["name"]
        columns = table.get("columns", [])
        
        sql_lines.append(f"CREATE TABLE IF NOT EXISTS {table_name} (")
        
        col_definitions = []
        foreign_keys = []
        
        for col in columns:
            col_name = col["name"]
            col_type = type_map.get(col["type"], "VARCHAR(255)")
            
            parts = [f"  {col_name} {col_type}"]
            
            if col.get("primary_key"):
                parts.append("PRIMARY KEY AUTOINCREMENT")
            if not col.get("nullable", True):
                parts.append("NOT NULL")
            if col.get("unique"):
                parts.append("UNIQUE")
                
            col_definitions.append(" ".join(parts))
            
            # Collect foreign keys separately
            fk = col.get("foreign_key")
            if fk and fk != "null" and fk is not None:
                ref_table, ref_col = fk.split(".")
                foreign_keys.append(
                    f"  FOREIGN KEY ({col_name}) REFERENCES {ref_table}({ref_col})"
                )
        
        all_definitions = col_definitions + foreign_keys
        sql_lines.append(",\n".join(all_definitions))
        sql_lines.append(");\n")
    
    return "\n".join(sql_lines)


def generate_api_stubs(api_schema: dict) -> str:
    """Takes the api_schema and generates Python FastAPI route stubs."""
    
    lines = []
    lines.append("# Auto-generated API stubs from App Compiler")
    lines.append("# Built with FastAPI - run with: uvicorn api:app --reload\n")
    lines.append("from fastapi import FastAPI, HTTPException, Depends")
    lines.append("from pydantic import BaseModel")
    lines.append("from typing import Optional\n")
    lines.append("app = FastAPI()\n")
    
    endpoints = api_schema.get("endpoints", [])
    
    for endpoint in endpoints:
        path = endpoint["path"]
        method = endpoint["method"].lower()
        description = endpoint.get("description", "")
        auth_required = endpoint.get("auth_required", False)
        
        # Generate a function name from the path
        func_name = path.replace("/", "_").replace("-", "_").strip("_")
        func_name = f"{method}_{func_name}"
        
        lines.append(f"@app.{method}('{path}')")
        
        if auth_required:
            lines.append(f"async def {func_name}():")
        else:
            lines.append(f"async def {func_name}():")
            
        lines.append(f'    """{ description }"""')
        lines.append(f"    # TODO: implement")
        lines.append(f"    pass\n")
    
    return "\n".join(lines)


def execute_schemas(final_schemas: dict, output_dir: str = ".") -> dict:
    """Main executor - takes final schemas and produces executable files."""
    
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    results = {}
    
    # Generate SQL
    db_schema = final_schemas.get("db_schema", {})
    if db_schema:
        sql = generate_sql(db_schema)
        sql_path = os.path.join(output_dir, "schema.sql")
        with open(sql_path, "w") as f:
            f.write(sql)
        results["sql"] = sql_path
        print(f"Generated SQL: {sql_path}")
    
    # Generate API stubs
    api_schema = final_schemas.get("api_schema", {})
    if api_schema:
        api_code = generate_api_stubs(api_schema)
        api_path = os.path.join(output_dir, "api.py")
        with open(api_path, "w") as f:
            f.write(api_code)
        results["api"] = api_path
        print(f"Generated API stubs: {api_path}")
    
    return results


# Test it
if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'pipeline'))
    
    from run_pipeline import run_pipeline
    
    prompt = "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."
    
    print("Running pipeline...")
    result = run_pipeline(prompt)
    
    print("\nGenerating executable files...")
    output = execute_schemas(result["final_schemas"], output_dir="generated_output")
    
    print("\nGenerated files:")
    for file_type, path in output.items():
        print(f"  {file_type}: {path}")
    
    # Print the SQL so we can see it
    print("\n--- Generated SQL ---")
    with open(output["sql"]) as f:
        print(f.read())