import requests
from concurrent.futures import ThreadPoolExecutor
import time
import sys
import os

# Calculate root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

BASE_URL = "http://localhost:8000"

def access_audit_dashboard(i):
    try:
        start = time.time()
        # Test the data endpoint which uses the DB connection
        resp = requests.get(f"{BASE_URL}/admin/auditoria/dados")
        duration = time.time() - start
        if resp.status_code == 200:
            print(f"Request {i}: Success ({duration:.3f}s)")
            return True
        else:
            print(f"Request {i}: Failed ({resp.status_code})")
            return False
    except Exception as e:
        print(f"Request {i}: Error {e}")
        return False

def run_stress_test():
    print("Starting Audit Dashboard Stress Test (10 concurrent requests)...")
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(access_audit_dashboard, range(10)))
    
    if all(results):
        print("PASS: All requests succeeded. Connection stable.")
    else:
        print("FAIL: Some requests failed.")

if __name__ == "__main__":
    run_stress_test()
