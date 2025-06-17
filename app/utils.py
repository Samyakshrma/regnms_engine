# app/utils.py
from uuid import uuid4
from datetime import datetime, UTC

def generate_id() -> str:
    return str(uuid4())

def current_timestamp():
    return datetime.now(UTC)
