import sys
import os

# Add Backend folder to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Backend"))

from app.main import app