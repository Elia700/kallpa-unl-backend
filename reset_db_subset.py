from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Drop tables in dependency order
    try:
        print("Dropping attendance...")
        db.session.execute(text("DROP TABLE IF EXISTS attendance CASCADE"))
        print("Dropping responsible...")
        db.session.execute(text("DROP TABLE IF EXISTS responsible CASCADE"))
        print("Dropping participant...")
        db.session.execute(text("DROP TABLE IF EXISTS participant CASCADE"))
        print("Dropping schedule...")
        db.session.execute(text("DROP TABLE IF EXISTS schedule CASCADE"))
        print("Dropping program...")
        db.session.execute(text("DROP TABLE IF EXISTS program CASCADE"))
        
        db.session.commit()
        print("Tables dropped.")
        
        print("Recreating tables...")
        db.create_all()
        print("Tables recreated.")
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
