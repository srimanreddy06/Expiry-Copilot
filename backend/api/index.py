import sys
import os

# Add the parent directory (backend/) to the path to resolve backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
