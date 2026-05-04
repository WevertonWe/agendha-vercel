import os
import sys

sys.path.append(os.path.dirname(__file__))

from app.main import app as main_app

app = main_app
