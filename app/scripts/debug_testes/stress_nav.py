import requests
import time
import os
import sys
from concurrent.futures import ThreadPoolExecutor

# Calculate root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

BASE_URL = "http://localhost:8000"

# List of pages to access (simulate user journey)
PAGES = [
    "/portal",
    "/oficios",
    "/financeiro/painel",
    "/admin/auditoria" # Check if navigating to audit logs itself is logged (meta-audit!)
]

def access_page(i):
    page = PAGES[i % len(PAGES)]
    start = time.time()
    try:
        resp = requests.get(f"{BASE_URL}{page}", cookies={"access_token": "mock_token"}) # Auth might fail but middleware runs before 401 response content generation? 
        # Actually middleware runs before response.
        # If accessing protected route without token, it redirects or returns 401. Middleware still logs ACESSO if it's GET.
        duration = time.time() - start
        return duration, resp.status_code
    except Exception as e:
        print(e)
        return 0, 500

def run_nav_stress():
    print("Starting Navigation Stress Test (50 Requests)...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(access_page, range(50)))
    
    total_time = sum(r[0] for r in results)
    avg_time = total_time / 50
    print(f"Average Response Time: {avg_time:.4f}s")
    
    if avg_time < 0.2:
        print("PASS: Latency < 200ms")
    else:
        print(f"WARN: Latency {avg_time:.4f}s")

if __name__ == "__main__":
    run_nav_stress()
