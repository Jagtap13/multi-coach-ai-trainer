import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "core"))
sys.path.append(os.path.join(os.path.dirname(__file__), "models"))

from database import Base, engine
from user import User

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")