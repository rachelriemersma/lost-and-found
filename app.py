from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

items = []

@app.route('/')
def home():
    return render_template('home.html', items=items)

@app.route('/post', methods=['GET', 'POST'])
def post_item():
    if request.method == 'POST':
        item = {
            'id': len(items) + 1,
            'title': request.form['title'],
            'description': request.form['description'],
            'category': request.form['category'],
            'location': request.form['location'],
            'contact': request.form['contact'],
            'date_posted': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        items.append(item)
        return redirect(url_for('home'))
    
    return render_template('post.html')

@app.route('/item/<int:item_id>')
def item_detail(item_id):
    item = next((item for item in items if item['id'] == item_id), None)
    return render_template('item_detail.html', item=item)

if __name__ == '__main__':
    app.run(debug=True)