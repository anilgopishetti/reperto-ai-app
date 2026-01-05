# app/database.py
import os
from sqlalchemy import create_engine, MetaData

# In-memory store for MVP
USERS_DB = {}  # {email: {name, email, password_hash}}

# Optional: Use SQLite if DATABASE_URL is provided
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./reperto_db.sqlite"
)

# For development with SQLite
try:
    if "sqlite" in DATABASE_URL:
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(DATABASE_URL)
    metadata = MetaData()
except Exception as e:
    print(f"Database connection warning: {e}. Using in-memory store.")
    engine = None
    metadata = None

# In-memory database object (simple dict)
class InMemoryDatabase:
    def __init__(self):
        self.connected = False
    
    async def connect(self):
        self.connected = True
    
    async def disconnect(self):
        self.connected = False

# Use in-memory database for MVP
database = InMemoryDatabase()
