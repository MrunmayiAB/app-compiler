import json
import time
import csv
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'pipeline'))
from run_pipeline import run_pipeline

# 10 normal prompts + 10 edge cases
TEST_PROMPTS = [
    # Normal prompts
    {"id": 1, "type": "normal", "prompt": "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."},
    {"id": 2, "type": "normal", "prompt": "Create an e-commerce store with product listings, shopping cart, checkout with payments, and order tracking. Admins manage inventory."},
    {"id": 3, "type": "normal", "prompt": "Build a blog platform where authors can write posts, readers can comment, and admins can moderate content."},
    {"id": 4, "type": "normal", "prompt": "Create a project management tool like Trello with boards, cards, team members, and due dates."},
    {"id": 5, "type": "normal", "prompt": "Build a food delivery app with restaurants, menus, orders, delivery tracking, and ratings."},
    {"id": 6, "type": "normal", "prompt": "Create a hotel booking system with room listings, reservations, payments, and reviews."},
    {"id": 7, "type": "normal", "prompt": "Build a learning management system where teachers create courses and students enroll and track progress."},
    {"id": 8, "type": "normal", "prompt": "Create a healthcare appointment booking app with doctors, patients, scheduling, and medical records."},
    {"id": 9, "type": "normal", "prompt": "Build a social media platform with posts, followers, likes, comments, and direct messages."},
    {"id": 10, "type": "normal", "prompt": "Create a gym management system with memberships, class schedules, trainers, and payment tracking."},

    # Edge cases
    {"id": 11, "type": "vague", "prompt": "Build me an app for my business."},
    {"id": 12, "type": "vague", "prompt": "I need a website."},
    {"id": 13, "type": "conflicting", "prompt": "Build an app where all users are admins but only admins have special access and regular users cannot see anything admins see."},
    {"id": 14, "type": "conflicting", "prompt": "Create a free app with premium features where everything is free but users must pay for everything."},
    {"id": 15, "type": "incomplete", "prompt": "Build a marketplace."},
    {"id": 16, "type": "incomplete", "prompt": "Create a booking system with payments."},
    {"id": 17, "type": "complex", "prompt": "Build a multi-tenant SaaS platform where each company gets their own isolated workspace, with SSO login, custom branding, role-based access, billing per seat, usage analytics, and an API for third-party integrations."},
    {"id": 18, "type": "complex", "prompt": "Create an AI-powered recruiting platform with job postings, applicant tracking, automated resume screening, interview scheduling, offer management, and analytics dashboards for HR teams."},
    {"id": 19, "type": "ambiguous", "prompt": "Build something like Airbnb but for cars and also for experiences and maybe hotels too."},
    {"id": 20, "type": "ambiguous", "prompt": "Create an app where people can share things and other people can see them and interact."},
]

def evaluate():
    results = []
    
    print(f"Running evaluation on {len(TEST_PROMPTS)} prompts...\n")
    
    for test in TEST_PROMPTS:
        print(f"[{test['id']}/20] Type: {test['type']}")
        print(f"Prompt: {test['prompt'][:60]}...")
        
        start_time = time.time()
        retries = 0
        success = False
        issues_found = 0
        repaired = False
        error_msg = ""
        
        try:
            result = run_pipeline(test["prompt"])
            validation = result["final_schemas"].get("_validation", {})
            
            success = True
            issues_found = validation.get("repair_count", 0)
            repaired = validation.get("repaired", False)
            
        except Exception as e:
            error_msg = str(e)[:100]
            retries = 1
            print(f"  Failed: {error_msg}")
        
        latency = round(time.time() - start_time, 2)
        
        results.append({
            "id": test["id"],
            "type": test["type"],
            "prompt": test["prompt"][:80],
            "success": success,
            "latency_seconds": latency,
            "issues_found": issues_found,
            "repaired": repaired,
            "retries": retries,
            "error": error_msg
        })
        
        status = "SUCCESS" if success else "FAILED"
        print(f"  {status} | {latency}s | Issues: {issues_found} | Repaired: {repaired}\n")
        
        # Wait between requests to avoid rate limits
        time.sleep(10)
    
    # Save to CSV
    with open("evaluation_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    # Print summary
    total = len(results)
    successes = sum(1 for r in results if r["success"])
    avg_latency = round(sum(r["latency_seconds"] for r in results) / total, 2)
    total_issues = sum(r["issues_found"] for r in results)
    
    print("\n=== EVALUATION SUMMARY ===")
    print(f"Success rate:     {successes}/{total} ({round(successes/total*100)}%)")
    print(f"Average latency:  {avg_latency}s")
    print(f"Total issues found & repaired: {total_issues}")
    print(f"Results saved to: evaluation_results.csv")

if __name__ == "__main__":
    evaluate()