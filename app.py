from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from firebase_config import db, auth_instance, firebase_admin
from firebase_admin import auth as admin_auth
from datetime import datetime, timedelta
import json
import uuid
import pytz

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

# Helper function to check if user is logged in
def is_logged_in():
    return 'user' in session

# Helper function to get current user
def get_current_user():
    if is_logged_in():
        return session['user']
    return None

# Routes
@app.route('/')
def index():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth_instance.sign_in_with_email_and_password(email, password)
            user_info = auth_instance.get_account_info(user['idToken'])
            session['user'] = {
                'token': user['idToken'],
                'email': email,
                'uid': user['localId'],
                'refreshToken': user['refreshToken']
            }
            
            # Get user role from Firestore
            user_doc = db.collection('users').document(user['localId']).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                session['user']['role'] = user_data.get('role', 'user')
            else:
                session['user']['role'] = 'user'
                
            return redirect(url_for('dashboard'))
        except Exception as e:
            return render_template('login.html', error='Invalid email or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        try:
            # Create user in Firebase Auth
            user = auth_instance.create_user_with_email_and_password(email, password)
            
            # Store additional user info in Firestore
            user_data = {
                'name': name,
                'email': email,
                'role': 'user',  # Default role
                'created_at': datetime.now(pytz.UTC)
            }
            db.collection('users').document(user['localId']).set(user_data)
            
            # Auto login after registration
            session['user'] = {
                'token': user['idToken'],
                'email': email,
                'uid': user['localId'],
                'refreshToken': user['refreshToken'],
                'role': 'user'
            }
            return redirect(url_for('dashboard'))
        except Exception as e:
            return render_template('register.html', error=str(e))
    return render_template('register.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        try:
            auth_instance.send_password_reset_email(email)
            return render_template('forgot-password.html', message='Password reset email sent! Check your inbox.')
        except Exception as e:
            return render_template('forgot-password.html', error='Email not found')
    return render_template('forgot-password.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    # Get counts for dashboard
    inventory_count = len(db.collection('inventory').get())
    loads_count = len(db.collection('loads').get())
    
    # Get expiring items (within 7 days)
    today = datetime.now(pytz.UTC)
    week_later = today + timedelta(days=7)
    
    expiring_items = []
    inventory_ref = db.collection('inventory').get()
    for doc in inventory_ref:
        item = doc.to_dict()
        if 'expiry_date' in item:
            expiry_date = datetime.strptime(item['expiry_date'], '%Y-%m-%d').replace(tzinfo=pytz.UTC)
            if today <= expiry_date <= week_later:
                item['id'] = doc.id
                expiring_items.append(item)
    
    # Get low stock items (less than 10 units)
    low_stock_items = []
    for doc in inventory_ref:
        item = doc.to_dict()
        if 'quantity' in item and int(item['quantity']) < 10:
            item['id'] = doc.id
            low_stock_items.append(item)
    
    return render_template('dashboard.html', 
                           user=get_current_user(),
                           inventory_count=inventory_count,
                           loads_count=loads_count,
                           expiring_items=expiring_items,
                           low_stock_items=low_stock_items)

@app.route('/inventory')
def inventory():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    inventory_ref = db.collection('inventory').get()
    items = []
    
    for doc in inventory_ref:
        item = doc.to_dict()
        item['id'] = doc.id
        items.append(item)
    
    return render_template('inventory.html', user=get_current_user(), items=items)

@app.route('/inventory/add', methods=['POST'])
def add_inventory():
    if not is_logged_in():
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    data = request.form
    
    item_data = {
        'name': data['name'],
        'category': data['category'],
        'quantity': int(data['quantity']),
        'unit': data['unit'],
        'expiry_date': data['expiry_date'],
        'added_by': session['user']['uid'],
        'added_at': datetime.now(pytz.UTC).isoformat(),
    }
    
    # Add item to Firestore
    db.collection('inventory').add(item_data)
    
    return redirect(url_for('inventory'))

@app.route('/inventory/update', methods=['POST'])
def update_inventory():
    if not is_logged_in():
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    item_id = request.form['id']
    data = request.form
    
    item_data = {
        'name': data['name'],
        'category': data['category'],
        'quantity': int(data['quantity']),
        'unit': data['unit'],
        'expiry_date': data['expiry_date'],
        'updated_at': datetime.now(pytz.UTC).isoformat(),
    }
    
    # Update item in Firestore
    db.collection('inventory').document(item_id).update(item_data)
    
    return redirect(url_for('inventory'))

@app.route('/inventory/delete', methods=['POST'])
def delete_inventory():
    if not is_logged_in():
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    item_id = request.form['id']
    
    # Delete item from Firestore
    db.collection('inventory').document(item_id).delete()
    
    return redirect(url_for('inventory'))

@app.route('/loads')
def loads():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    loads_ref = db.collection('loads').get()
    loads_list = []
    
    for doc in loads_ref:
        load = doc.to_dict()
        load['id'] = doc.id
        loads_list.append(load)
    
    return render_template('loads.html', user=get_current_user(), loads=loads_list)

@app.route('/loads/add', methods=['POST'])
def add_load():
    if not is_logged_in():
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    data = request.form
    
    load_data = {
        'destination': data['destination'],
        'description': data['description'],
        'status': data['status'],
        'estimated_delivery': data['estimated_delivery'],
        'items': json.loads(data['items']),
        'created_by': session['user']['uid'],
        'created_at': datetime.now(pytz.UTC).isoformat(),
    }
    
    # Add load to Firestore
    db.collection('loads').add(load_data)
    
    # Update inventory quantities
    for item in load_data['items']:
        inventory_doc = db.collection('inventory').document(item['id']).get()
        if inventory_doc.exists:
            current_quantity = inventory_doc.to_dict()['quantity']
            new_quantity = current_quantity - int(item['quantity'])
            db.collection('inventory').document(item['id']).update({'quantity': new_quantity})
    
    return redirect(url_for('loads'))

@app.route('/loads/update', methods=['POST'])
def update_load():
    if not is_logged_in():
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    load_id = request.form['id']
    data = request.form
    
    load_data = {
        'destination': data['destination'],
        'description': data['description'],
        'status': data['status'],
        'estimated_delivery': data['estimated_delivery'],
        'updated_at': datetime.now(pytz.UTC).isoformat(),
    }
    
    # Update load in Firestore
    db.collection('loads').document(load_id).update(load_data)
    
    return redirect(url_for('loads'))

@app.route('/loads/delete', methods=['POST'])
def delete_load():
    if not is_logged_in():
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    load_id = request.form['id']
    
    # Get the load data first to restore inventory quantities
    load_doc = db.collection('loads').document(load_id).get()
    if load_doc.exists:
        load_data = load_doc.to_dict()
        
        # Only restore inventory if the load wasn't delivered
        if load_data.get('status') != 'Delivered' and 'items' in load_data:
            for item in load_data['items']:
                inventory_doc = db.collection('inventory').document(item['id']).get()
                if inventory_doc.exists:
                    current_quantity = inventory_doc.to_dict()['quantity']
                    new_quantity = current_quantity + int(item['quantity'])
                    db.collection('inventory').document(item['id']).update({'quantity': new_quantity})
    
    # Delete load from Firestore
    db.collection('loads').document(load_id).delete()
    
    return redirect(url_for('loads'))

@app.route('/reports')
def reports():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    # Get total inventory value
    inventory_ref = db.collection('inventory').get()
    total_items = len(inventory_ref)
    
    # Get completed loads
    loads_ref = db.collection('loads').where('status', '==', 'Delivered').get()
    completed_loads = len(loads_ref)
    
    # Calculate expiration prevention
    today = datetime.now(pytz.UTC)
    prevented_waste = 0
    
    for doc in inventory_ref:
        item = doc.to_dict()
        if 'expiry_date' in item:
            expiry_date = datetime.strptime(item['expiry_date'], '%Y-%m-%d').replace(tzinfo=pytz.UTC)
            if (expiry_date - today).days <= 7 and (expiry_date - today).days > 0:
                prevented_waste += 1
    
    return render_template('reports.html', 
                           user=get_current_user(),
                           total_items=total_items,
                           completed_loads=completed_loads,
                           prevented_waste=prevented_waste)

if __name__ == '__main__':
    app.run(debug=True)