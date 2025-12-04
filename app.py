from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
import string
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

database_url = os.environ.get('DATABASE_URL', 'sqlite:///lost_and_found.db')

if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_deletion_code():
    """Generate a random 6-character code for item deletion"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    deletion_code = db.Column(db.String(20), nullable=False)
    image_filename = db.Column(db.String(200))
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
        
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
        
        item = Item(
            title=request.form['title'],
            description=request.form['description'],
            category=request.form['category'],
            location=request.form['location'],
            contact=request.form['contact'],
            deletion_code=deletion_code,
            image_filename=image_filename
        )
        db.session.add(item)
        db.session.commit()
        
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
            if item.image_filename:
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], item.image_filename)
                if os.path.exists(image_path):
                    os.remove(image_path)
            
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

# Create tables on startup
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
