from app import app, db, Item
import os

# Delete old database
db_path = 'instance/lost_and_found.db'
if os.path.exists(db_path):
    os.remove(db_path)
    print("Old database deleted.")

# Create new database with updated schema
with app.app_context():
    db.create_all()
    print("New database created - empty and ready to use!")

print("\nDatabase reset complete!")