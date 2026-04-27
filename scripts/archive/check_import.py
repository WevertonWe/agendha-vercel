
import sys
sys.path.append("c:/Wev Dev/projetos/agendha")

try:
    print("Importing router module...")
    from app.core.auth import router
    print("Router module imported.")
    
    if hasattr(router, 'get_password_hash'):
        print("SUCCESS: get_password_hash found in router module namespace.")
    else:
        # Check if it is in the global scope of the module
        import inspect
        if 'get_password_hash' in dict(inspect.getmembers(router)):
             print("SUCCESS: get_password_hash found via inspect.")
        else:
             print("FAILURE: get_password_hash NOT found in router module.")
except Exception as e:
    print(f"Import Error: {e}")
