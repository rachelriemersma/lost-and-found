from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lost_and_found.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def generate_deletion_code():
    """Generate a random 6-character code for item deletion"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Database Model
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    deletion_code = db.Column(db.String(20), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Item {self.title}>'

@app.route('/')
def home():
    items = Item.query.order_by(Item.date_posted.desc()).all()
    return render_template('home.html', items=items)

@app.route('/post', methods=['GET', 'POST'])
def post_item():
    if request.method == 'POST':
        deletion_code = generate_deletion_code()
        item = Item(
            title=request.form['title'],
            description=request.form['description'],
            category=request.form['category'],
            location=request.form['location'],
            contact=request.form['contact'],
            deletion_code=deletion_code
        )
        db.session.add(item)
        db.session.commit()
        
        # Store the deletion code in session to show it to the user
        session['last_deletion_code'] = deletion_code
        session['last_item_id'] = item.id
        
        return redirect(url_for('post_success'))
    
    return render_template('post.html')

@app.route('/post-success')
def post_success():
    deletion_code = session.get('last_deletion_code')
    item_id = session.get('last_item_id')
    
    if not deletion_code or not item_id:
        return redirect(url_for('home'))
    
    # Clear session after displaying
    session.pop('last_deletion_code', None)
    session.pop('last_item_id', None)
    
    return render_template('post_success.html', deletion_code=deletion_code, item_id=item_id)

@app.route('/delete', methods=['GET', 'POST'])
def delete_item():
    if request.method == 'POST':
        item_id = request.form.get('item_id')
        deletion_code = request.form.get('deletion_code')
        
        item = Item.query.get(item_id)
        
        if item and item.deletion_code == deletion_code:
            db.session.delete(item)
            db.session.commit()
            flash('Item successfully marked as found and removed!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid item ID or deletion code. Please try again.', 'error')
            return redirect(url_for('delete_item'))
    
    return render_template('delete.html')

@app.route('/item/<int:item_id>')
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template('item_detail.html', item=item)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)