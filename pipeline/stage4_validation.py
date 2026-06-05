from google import genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def validate_and_repair(schemas: dict) -> dict:
    
    # Step 1: Run rule-based checks first (no LLM needed for these)
    issues = []
    
    db_tables = [t["name"] for t in schemas.get("db_schema", {}).get("tables", [])]
    api_paths = [e["path"] for e in schemas.get("api_schema", {}).get("endpoints", [])]
    ui_pages = [p["name"] for p in schemas.get("ui_schema", {}).get("pages", [])]
    auth_roles = [r["role"] for r in schemas.get("auth_rules", {}).get("rules", [])]
    
    # Check 1: Every DB table should have at least one API endpoint
    for table in db_tables:
        # Convert table name to expected API path pattern
        has_endpoint = any(table.rstrip("s") in path or table in path 
                          for path in api_paths)
        if not has_endpoint:
            issues.append(f"DB table '{table}' has no corresponding API endpoint")
    
    # Check 2: Every page should have a route
    for page in schemas.get("ui_schema", {}).get("pages", []):
        if "route" not in page or not page["route"]:
            issues.append(f"UI page '{page['name']}' is missing a route")
    
    # Check 3: Auth rules should cover all roles from UI pages
    ui_roles = set()
    for page in schemas.get("ui_schema", {}).get("pages", []):
        for role in page.get("accessible_by", []):
            ui_roles.add(role)
    
    for role in ui_roles:
        if role not in auth_roles:
            issues.append(f"Role '{role}' used in UI but missing from auth rules")
    
    # Check 4: Foreign keys should reference existing tables
    for table in schemas.get("db_schema", {}).get("tables", []):
        for col in table.get("columns", []):
            fk = col.get("foreign_key")
            if fk and fk != "null" and fk is not None:
                referenced_table = fk.split(".")[0]
                if referenced_table not in db_tables:
                    issues.append(f"Foreign key '{fk}' in table '{table['name']}' references non-existent table")
    
    print(f"Found {len(issues)} issues:")
    for issue in issues:
        print(f"  - {issue}")
    
    # Step 2: If issues found, use LLM to repair
    if issues:
        print("\nRepairing issues...")
        repaired = repair_schemas(schemas, issues)
        repaired["_validation"] = {
            "issues_found": issues,
            "repaired": True,
            "repair_count": len(issues)
        }
        return repaired
    else:
        schemas["_validation"] = {
            "issues_found": [],
            "repaired": False,
            "repair_count": 0
        }
        return schemas


def repair_schemas(schemas: dict, issues: list) -> dict:
    
    prompt = f"""
You are the validation and repair layer of an app-generation compiler.
The following schemas have been generated but contain inconsistencies.

Current schemas:
{json.dumps(schemas, indent=2)}

Issues detected:
{json.dumps(issues, indent=2)}

Fix ALL the listed issues and return the complete corrected schemas.
Return ONLY the valid JSON with the same structure as the input schemas.
Do not change anything that isn't broken.
No explanation, no markdown, no code blocks.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    raw = response.text.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw)


if __name__ == "__main__":
    from stage1_intent import extract_intent
    from stage2_design import design_system
    from stage3_schemas import generate_schemas

    test_prompt = "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."

    print("Stage 1: Extracting intent...")
    intent = extract_intent(test_prompt)
    print("Done.\n")

    print("Stage 2: Designing system...")
    design = design_system(intent)
    print("Done.\n")

    print("Stage 3: Generating schemas...")
    schemas = generate_schemas(design)
    print("Done.\n")

    print("Stage 4: Validating and repairing...")
    final = validate_and_repair(schemas)
    
    print("\nValidation summary:")
    print(json.dumps(final["_validation"], indent=2))