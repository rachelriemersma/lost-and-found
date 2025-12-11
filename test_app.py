"""
Test Suite for Campus Lost & Found Application

Run tests with: pytest test_app.py -v
"""

import pytest
import os
from app import app, db, Item
from datetime import datetime


@pytest.fixture
def client():
    """Create a test client with in-memory database"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


@pytest.fixture
def sample_item():
    """Create a sample item for testing"""
    return {
        'title': 'Test Lost iPhone',
        'description': 'Black iPhone 13 with cracked screen',
        'category': 'Electronics',
        'location': 'Library 2nd Floor',
        'contact': 'test@example.com'
    }


def test_home_page_loads(client):
    """Test that home page loads successfully"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Campus Lost & Found' in response.data


def test_post_page_loads(client):
    """Test that post item page loads"""
    response = client.get('/post')
    assert response.status_code == 200
    assert b'Post a Lost or Found Item' in response.data


def test_delete_page_loads(client):
    """Test that mark as found page loads"""
    response = client.get('/delete')
    assert response.status_code == 200
    assert b'Mark Item as Found' in response.data


def test_post_item_valid(client, sample_item):
    """Test posting a valid item"""
    response = client.post('/post', data=sample_item, follow_redirects=True)
    assert response.status_code == 200
    assert b'Item Posted Successfully' in response.data or b'deletion' in response.data.lower()


def test_post_item_creates_database_entry(client, sample_item):
    """Test that posting creates a database entry"""
    with app.app_context():
        initial_count = Item.query.count()
    
    client.post('/post', data=sample_item)
    
    with app.app_context():
        final_count = Item.query.count()
        assert final_count == initial_count + 1


def test_posted_item_appears_on_home(client, sample_item):
    """Test that posted item appears on home page"""
    client.post('/post', data=sample_item)
    response = client.get('/')
    assert response.status_code == 200
    assert sample_item['title'].encode() in response.data


def test_deletion_code_generated(client, sample_item):
    """Test that deletion code is generated and displayed"""
    response = client.post('/post', data=sample_item, follow_redirects=True)
    # Check for 6-character alphanumeric pattern or presence of deletion code text
    assert b'deletion' in response.data.lower() or b'code' in response.data.lower()


def test_view_item_detail(client, sample_item):
    """Test viewing item details"""
    # First post an item
    client.post('/post', data=sample_item)
    
    # Get the item ID
    with app.app_context():
        item = Item.query.first()
        item_id = item.id
    
    # View the item
    response = client.get(f'/item/{item_id}')
    assert response.status_code == 200
    assert sample_item['title'].encode() in response.data
    assert sample_item['description'].encode() in response.data


def test_view_nonexistent_item_returns_404(client):
    """Test that viewing non-existent item returns 404"""
    response = client.get('/item/99999')
    assert response.status_code == 404


def test_delete_item_with_valid_code(client, sample_item):
    """Test deleting item with correct deletion code"""
    # Post an item
    client.post('/post', data=sample_item)
    
    # Get the item and deletion code
    with app.app_context():
        item = Item.query.first()
        item_id = item.id
        deletion_code = item.deletion_code
    
    # Delete the item
    response = client.post('/delete', data={
        'item_id': item_id,
        'deletion_code': deletion_code
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'successfully' in response.data.lower() or b'removed' in response.data.lower()
    
    # Verify item is deleted
    with app.app_context():
        item = Item.query.get(item_id)
        assert item is None


def test_delete_item_with_invalid_code(client, sample_item):
    """Test that deletion fails with wrong code"""
    # Post an item
    client.post('/post', data=sample_item)
    
    # Get the item ID
    with app.app_context():
        item = Item.query.first()
        item_id = item.id
    
    # Try to delete with wrong code
    response = client.post('/delete', data={
        'item_id': item_id,
        'deletion_code': 'WRONG1'
    }, follow_redirects=True)
    
    assert b'Invalid' in response.data or b'error' in response.data.lower()
    
    # Verify item still exists
    with app.app_context():
        item = Item.query.get(item_id)
        assert item is not None


def test_delete_nonexistent_item(client):
    """Test deleting non-existent item returns error"""
    response = client.post('/delete', data={
        'item_id': 99999,
        'deletion_code': 'ABC123'
    }, follow_redirects=True)
    
    assert b'Invalid' in response.data or b'error' in response.data.lower()

def test_item_model_creation():
    """Test Item model can be instantiated"""
    item = Item(
        title='Test Item',
        description='Test Description',
        category='Electronics',
        location='Library',
        contact='test@example.com',
        deletion_code='ABC123'
    )
    assert item.title == 'Test Item'
    assert item.deletion_code == 'ABC123'


def test_item_model_repr():
    """Test Item model string representation"""
    item = Item(
        title='Test Item',
        description='Test',
        category='Electronics',
        location='Library',
        contact='test@example.com',
        deletion_code='ABC123'
    )
    assert 'Test Item' in repr(item)

def test_sql_injection_prevention(client):
    """Test that SQL injection attempts are escaped"""
    malicious_data = {
        'title': "'; DROP TABLE item; --",
        'description': 'Test',
        'category': 'Electronics',
        'location': 'Library',
        'contact': 'test@example.com'
    }
    
    client.post('/post', data=malicious_data)
    
    # Verify table still exists and item was created safely
    with app.app_context():
        items = Item.query.all()
        assert len(items) > 0
        assert items[0].title == "'; DROP TABLE item; --"


def test_xss_prevention(client):
    """Test that XSS attempts are escaped"""
    xss_data = {
        'title': 'Test Item',
        'description': '<script>alert("XSS")</script>',
        'category': 'Electronics',
        'location': 'Library',
        'contact': 'test@example.com'
    }
    
    client.post('/post', data=xss_data)
    
    with app.app_context():
        item = Item.query.first()
        item_id = item.id
    
    response = client.get(f'/item/{item_id}')
    # Script should be escaped, not executed
    assert b'&lt;script&gt;' in response.data or b'<script>' not in response.data

def test_empty_database_shows_message(client):
    """Test that empty database shows appropriate message"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'No items posted yet' in response.data or b'first to post' in response.data.lower()

def test_multiple_items_ordering(client, sample_item):
    """Test that items are ordered by date (newest first)"""
    # Post first item
    client.post('/post', data=sample_item)
    
    # Post second item
    second_item = sample_item.copy()
    second_item['title'] = 'Second Item'
    client.post('/post', data=second_item)
    
    # Check ordering
    with app.app_context():
        items = Item.query.order_by(Item.date_posted.desc()).all()
        assert items[0].title == 'Second Item'
        assert items[1].title == 'Test Lost iPhone'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])