from google import genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def extract_intent(user_prompt: str) -> dict:
    
    prompt = f"""
You are the first stage of an app-generation compiler.
Your job is to extract structured intent from a user's natural language description.

User input: "{user_prompt}"

Return ONLY a valid JSON object with exactly these fields:
{{
  "app_type": "what kind of app this is (e.g. CRM, E-commerce, Blog)",
  "features": ["list", "of", "features", "mentioned"],
  "entities": ["list", "of", "data", "entities", "e.g. User, Product, Order"],
  "roles": ["list", "of", "user", "roles", "e.g. Admin, Customer"],
  "constraints": ["list", "of", "business", "rules", "or", "constraints"],
  "ambiguities": ["list", "of", "anything", "unclear", "or", "underspecified"]
}}

Rules:
- Return ONLY the JSON, no explanation, no markdown, no code blocks
- Every field must be present even if the list is empty
- Infer reasonable values if not explicitly stated
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )
    
    raw = response.text.strip()
    
    # Remove markdown code blocks if Gemini adds them anyway
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    
    result = json.loads(raw)
    return result


# Test it
if __name__ == "__main__":
    test_prompt = "Build me an app for my business."
    
    print("Input:", test_prompt)
    print("\nExtracting intent...\n")
    
    result = extract_intent(test_prompt)
    print(json.dumps(result, indent=2))
