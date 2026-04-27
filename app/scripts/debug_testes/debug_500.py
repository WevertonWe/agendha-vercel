import requests

BASE_URL = "http://localhost:8000"

def debug_request():
    print("Debug Request...")
    try:
        resp = requests.get(f"{BASE_URL}/admin/auditoria/dados")
        print(f"Status: {resp.status_code}")
        if resp.status_code == 500:
            print("Response Content:")
            print(resp.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_request()
