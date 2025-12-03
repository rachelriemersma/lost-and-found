# Campus Lost & Found Web Application

## Project Overview
A web-based Lost & Found platform for Loyola University Chicago campus where students can post lost or found items with images, browse items, and mark them as found when recovered.
### Backend
- **Flask 3.0.0**: Python web framework for handling HTTP requests and routing
- **SQLAlchemy 3.1.1**: ORM (Object-Relational Mapping) for database operations
- **SQLite**: Lightweight relational database for data persistence

### Frontend
- **Jinja2**: Template engine for dynamic HTML rendering
- **HTML5/CSS3**: Modern web standards

### Security & File Handling
- **Werkzeug**: Secure filename sanitization for uploads
- **Flask Sessions**: Server-side session management for deletion codes

## Key Features

### 1. Post Items
**How it works:**
- User fills out form with item details
- Optional image upload (validated for file type and size)
- System generates unique Item ID and 6-character deletion code
- Item saved to database, image saved to `static/uploads/`
- User receives success page with their codes (shown only once)

**Technical details:**
- Form data validated server-side
- Images: Max 16MB, allowed types: JPG, PNG, GIF
- Filenames timestamped to prevent conflicts
- Database transaction ensures data integrity

### 2. Browse Items
**How it works:**
- Home page queries database for all items
- Items displayed in grid layout, sorted by newest first
- Each card shows image, title, category, location, date

**Technical details:**
- SQL query: `SELECT * FROM item ORDER BY date_posted DESC`
- Jinja2 templates render cards dynamically
- CSS Grid for responsive layout

### 3. View Item Details
**How it works:**
- Click "View Details" to see full information
- Shows complete description, contact info, and Item ID

**Technical details:**
- Route: `/item/<id>` extracts ID from URL
- Database lookup using primary key (fast)
- 404 error if item doesn't exist

### 4. Mark as Found (Delete)
**How it works:**
- User enters Item ID and deletion code
- System validates both match database record
- If correct, deletes item and associated image file
- If incorrect, shows error message

**Technical details:**
- Authorization check: `if item.deletion_code == user_input`
- Cascading delete: removes database record + image file
- Flash messages for user feedback

### 5. Image Upload System
**How it works:**
- User selects image file
- Backend validates file type and size
- File saved with unique timestamp-based name
- Filename stored in database

**Technical details:**
```python
# Validation
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Secure filename generation
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f"{timestamp}_{secure_filename(original_name)}"
```

## Database Schema
```sql
Table: item
├── id (INTEGER, Primary Key, Auto-increment)
├── title (VARCHAR(100), Required)
├── description (TEXT, Required)
├── category (VARCHAR(50), Required)
├── location (VARCHAR(100), Required)
├── contact (VARCHAR(100), Required)
├── deletion_code (VARCHAR(20), Required)
├── image_filename (VARCHAR(200), Optional)
└── date_posted (DATETIME, Required, Default: Current time)
```