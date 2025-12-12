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


## Planned Enhancements and Future Work

The current implementation focuses on delivering core Lost & Found functionality in a clear and reliable manner. The following enhancements were identified during development but were not completed within the scope of this project:

### 1. User Authentication (Login & Registration)
Adding user accounts would allow posters to authenticate themselves and manage their own listings. This would enable features such as editing posts, viewing posting history, and improved ownership validation beyond deletion codes.

### 2. API Endpoints for Mobile Integration
Developing RESTful API endpoints would allow the backend to support mobile applications or third-party clients. This would make the system more extensible and enable cross-platform access.

### 3. Database Migration and Scalability Support
The project currently uses SQLite for simplicity and ease of setup. Future versions could support more scalable database systems such as PostgreSQL or MySQL, along with database migration tooling to manage schema changes in production environments.

### 4. Expanded Automated Testing
While basic automated tests are included, the test suite could be expanded to cover additional routes, edge cases, and error conditions. Increased test coverage would improve long-term reliability and maintainability.

### 5. Pagination and Tagging for Item Searches
As the number of posted items grows, pagination would improve performance and usability. Adding tags or advanced filtering (e.g., by category or location) would further enhance the browsing and search experience.

These planned enhancements represent logical next steps for extending the project and improving its usability, scalability, and robustness.


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
