from google import genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def design_system(intent: dict) -> dict:
    
    prompt = f"""
You are the system design layer of an app-generation compiler.
You receive structured intent and produce a complete system architecture.

Input intent:
{json.dumps(intent, indent=2)}

Return ONLY a valid JSON object with exactly these fields:
{{
  "modules": [
    {{
      "name": "module name e.g. AuthModule",
      "description": "what this module does",
      "responsibilities": ["list", "of", "responsibilities"]
    }}
  ],
  "entities": [
    {{
      "name": "entity name e.g. User",
      "fields": [
        {{
          "name": "field name e.g. email",
          "type": "string | integer | boolean | datetime | float | text",
          "required": true,
          "unique": false
        }}
      ],
      "relations": [
        {{
          "type": "has_many | belongs_to | has_one",
          "entity": "related entity name"
        }}
      ]
    }}
  ],
  "user_flows": [
    {{
      "name": "flow name e.g. Login Flow",
      "steps": ["step 1", "step 2", "step 3"]
    }}
  ],
  "auth": {{
    "type": "JWT",
    "roles": ["list of roles"],
    "permissions": {{
      "role_name": ["list", "of", "allowed", "actions"]
    }}
  }}
}}

Rules:
- Return ONLY the JSON, no explanation, no markdown, no code blocks
- Every entity must have an id field (integer, required, unique)
- Relations must be consistent (if User has_many Orders, Order must belongs_to User)
- Permissions must cover all roles defined
- Be thorough and complete - this will drive code generation
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


# Test it by chaining with Stage 1
if __name__ == "__main__":
    from stage1_intent import extract_intent
    
    test_prompt = "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."
    
    print("Stage 1: Extracting intent...")
    intent = extract_intent(test_prompt)
    print("Done.\n")
    
    print("Stage 2: Designing system...")
    design = design_system(intent)
    print(json.dumps(design, indent=2))