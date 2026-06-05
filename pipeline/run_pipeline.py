import json
from stage1_intent import extract_intent
from stage2_design import design_system
from stage3_schemas import generate_schemas
from stage4_validation import validate_and_repair

def run_pipeline(user_prompt: str) -> dict:
    
    print("Stage 1: Extracting intent...")
    intent = extract_intent(user_prompt)
    
    print("Stage 2: Designing system...")
    design = design_system(intent)
    
    print("Stage 3: Generating schemas...")
    schemas = generate_schemas(design)
    
    print("Stage 4: Validating and repairing...")
    final = validate_and_repair(schemas)
    
    return {
        "intent": intent,
        "design": design,
        "final_schemas": final
    }

if __name__ == "__main__":
    prompt = "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."
    result = run_pipeline(prompt)
    print("\n✅ Pipeline complete!")
    print(json.dumps(result["final_schemas"]["_validation"], indent=2))