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
    print("New database created with deletion_code field.")
    
    # Add sample items with deletion codes
    sample_items = [
        Item(
            title="Lost iPhone 13",
            description="Black iPhone 13 with cracked screen",
            category="Electronics",
            location="Library 2nd Floor",
            contact="john@example.com",
            deletion_code="ABC123"
        ),
        Item(
            title="Found Blue Backpack",
            description="Blue Nike backpack with textbooks inside",
            category="Other",
            location="Student Center",
            contact="jane@example.com",
            deletion_code="XYZ789"
        ),
        Item(
            title="Lost Student ID",
            description="Student ID for Alex Johnson",
            category="ID/Cards",
            location="Gym",
            contact="alex@example.com",
            deletion_code="DEF456"
        )
    ]
    
    for item in sample_items:
        db.session.add(item)
    
    db.session.commit()
    print(f"Added {len(sample_items)} sample items.")
    
    # Display all items with their deletion codes
    print("\nSample items (for testing):")
    all_items = Item.query.all()
    for item in all_items:
        print(f"- ID {item.id}: {item.title} | Deletion code: {item.deletion_code}")

print("\nDatabase reset complete!")