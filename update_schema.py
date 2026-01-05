from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE schedule ADD COLUMN status VARCHAR(20) DEFAULT 'active'"))
            conn.commit()
        print("Schema updated successfully: Added 'status' column to 'schedule' table.")
    except Exception as e:
        print(f"Error updating schema: {e}")
