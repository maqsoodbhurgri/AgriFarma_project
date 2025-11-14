"""
Quick migration script to add reputation_score to users table
"""
from app import app
from agrifarma.extensions import db
from sqlalchemy import text

with app.app_context():
    try:
        # Try to add the column
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE users ADD COLUMN reputation_score INTEGER DEFAULT 0'))
            conn.commit()
        print("✓ Successfully added reputation_score column to users table")
    except Exception as e:
        if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
            print("✓ Column reputation_score already exists")
        else:
            print(f"✗ Error: {e}")

