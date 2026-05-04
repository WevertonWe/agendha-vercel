import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.main import app as main_app # noqa: F401
