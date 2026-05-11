import os
import sys
import traceback

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

try:
    from app.main import app as main_app
    app = main_app
except Exception as e:
    print("CRITICAL BOOT ERROR IN VERCEL:")
    traceback.print_exc()
    raise e
