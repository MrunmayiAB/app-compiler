from google import genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_schemas(design: dict) -> dict:

    prompt = f"""
You are the schema generation layer of an app-generation compiler.
You receive a system design and generate four complete schemas.

Input design:
{json.dumps(design, indent=2)}

Return ONLY a valid JSON object with exactly these fields:
{{
  "db_schema": {{
    "tables": [
      {{
        "name": "table name e.g. users",
        "columns": [
          {{
            "name": "column name",
            "type": "INTEGER | VARCHAR | TEXT | BOOLEAN | DATETIME | FLOAT",
            "primary_key": false,
            "nullable": false,
            "unique": false,
            "foreign_key": "referenced_table.column or null"
          }}
        ]
      }}
    ]
  }},
  "api_schema": {{
    "endpoints": [
      {{
        "path": "/api/resource",
        "method": "GET | POST | PUT | DELETE",
        "description": "what this endpoint does",
        "auth_required": true,
        "allowed_roles": ["Admin", "User"],
        "request_body": {{"field": "type"}},
        "response": {{"field": "type"}}
      }}
    ]
  }},
  "ui_schema": {{
    "pages": [
      {{
        "name": "page name e.g. LoginPage",
        "route": "/route",
        "accessible_by": ["Admin", "User"],
        "components": [
          {{
            "type": "form | table | chart | card | navbar | button",
            "name": "component name",
            "fields": ["list of fields shown or used"]
          }}
        ]
      }}
    ]
  }},
  "auth_rules": {{
    "strategy": "JWT",
    "token_expiry": "24h",
    "rules": [
      {{
        "role": "role name",
        "can_access": ["list of routes"],
        "cannot_access": ["list of routes"],
        "special_permissions": ["any extra permissions"]
      }}
    ]
  }}
}}

Rules:
- Return ONLY the JSON, no explanation, no markdown, no code blocks
- Every table must have an id column (INTEGER, primary_key: true)
- API paths must match DB tables (e.g. users table → /api/users endpoint)
- UI pages must use fields that exist in the API responses
- Auth rules must cover every role in the design
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

    result = json.loads(raw)
    return result


if __name__ == "__main__":
    from stage1_intent import extract_intent
    from stage2_design import design_system

    test_prompt = "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."

    print("Stage 1: Extracting intent...")
    intent = extract_intent(test_prompt)
    print("Done.\n")

    print("Stage 2: Designing system...")
    design = design_system(intent)
    print("Done.\n")

    print("Stage 3: Generating schemas...")
    schemas = generate_schemas(design)
    print(json.dumps(schemas, indent=2))