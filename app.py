from flask import Flask, render_template, request, redirect, url_for
from flask_bcrypt import generate_password_hash, check_password_hash
from flask import session
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()  # take environment variables from .env.
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# MongoDB Atlas connection string (replace with your own)
MONGO_URI = os.getenv('MONGO_URI')

# Initialize the database and collections
db = None
income_collection = None
expenses_collection = None
assets_collection = None
liabilities_collection = None
users_collection = None
try:
    # Create a MongoClient instance
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)  # Timeout after 5 seconds
    
    # Check the connection by sending a ping to the server
    client.admin.command('ping')
    
    print("Successfully connected to MongoDB!")
    
    # Get the database and collections
    db = client.financial_database
    income_collection = db.income
    expenses_collection = db.expenses
    assets_collection = db.assets
    liabilities_collection = db.liabilities
    users_collection = db.users

except ConnectionFailure:
    print("Failed to connect to MongoDB. Please check your connection string and network connectivity.")

# In your Flask app, define a filter function
def number_format(value, format="{:,.2f}"):
    return format.format(value)

# Register the filter with the Jinja environment
app.jinja_env.filters['number_format'] = number_format

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))    
    
    # Get the incomes associated with the user
    user_id = ObjectId(session['user_id'])

    income_categories = []
    total_income = 0
    if income_collection is not None:
        income_categories = list(income_collection.find({"user_id": user_id}))
        print(income_categories)
        total_income = sum(category['income_amount'] for category in income_categories)
        print("Total Income:", total_income)

    expenses_categories = []
    total_expenses = 0
    if expenses_collection is not None:
        expenses_categories = list(expenses_collection.find({"user_id": user_id}))
        print(expenses_categories)
        total_expenses = sum(category['expenses_amount'] for category in expenses_categories)
        print("Total Expenses:", total_expenses)

    assets_categories = []
    total_assets = 0
    if assets_collection is not None:
        assets_categories = list(assets_collection.find({"user_id": user_id}))
        print(assets_categories)
        total_assets = sum(category['asset_amount'] for category in assets_categories)
        print("Total Expenses:", total_assets)

    liabilities_categories = []
    total_liabilities = 0
    if liabilities_collection is not None:
        liabilities_categories = list(liabilities_collection.find({"user_id": user_id}))
        print(liabilities_categories)
        total_liabilities = sum(category['liability_amount'] for category in liabilities_categories)
        print("Total Expenses:", total_liabilities)

    net_worth = total_assets - total_liabilities

    return render_template('index.html', income_categories=income_categories, total_income=total_income, expenses_categories=expenses_categories, total_expenses=total_expenses, assets_categories=assets_categories, total_assets=total_assets, liabilities_categories=liabilities_categories, total_liabilities=total_liabilities, net_worth=net_worth)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Hash the password
        hashed_pw = generate_password_hash(password).decode('utf-8')

        # Insert the new user into the database
        users_collection.insert_one({
            "username": username,
            "password_hash": hashed_pw,
            "email": email
        })

        # Redirect to the login page, or auto-login the user
        return redirect(url_for('login'))
    
    # If it's a GET request, render the registration template
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Find the user by username
        user = users_collection.find_one({"username": username})

        if user and check_password_hash(user['password_hash'], password):
            # After validating credentials
            session['logged_in'] = True             
            # If the user is found and password is correct:
            session['user_id'] = str(user['_id'])
            return redirect(url_for('index'))
        else:
            # If user is not found or password is wrong
            # Show an error message or flash a message to the user
            pass
    
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)  # Remove logged_in from session    
    session.pop('user_id', None)  # Remove user_id from session
    return redirect(url_for('index'))

@app.route('/add_income', methods=['GET', 'POST'])
def add_income():
    if request.method == 'POST':
        # Only allow logged in users to add income
        if 'user_id' not in session:
            return redirect(url_for('login'))

        # Retrieve the income details from form
        income_details = {
            "user_id": ObjectId(session['user_id']),
            "income_name": request.form['income_name'],
            "income_category": request.form['income_category'],
            "income_amount": float(request.form['income_amount'])
        }
        income_collection.insert_one(income_details)
        return redirect(url_for('index'))
    
    # For GET requests, just render the add income form
    return render_template('add_income.html')

@app.route('/update_income/<category_id>', methods=['GET', 'POST'])
def update_income(category_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = ObjectId(session['user_id'])
    
    if request.method == 'POST':
        category = income_collection.find_one({'_id': ObjectId(category_id), 'user_id': user_id})

        if category is None:
            return "Income not found or you do not have permission to edit it", 403
    
        income_name = request.form['income_name']
        income_category = request.form['income_category']
        income_amount = float(request.form['income_amount'])
        
        income_collection.update_one({'_id': ObjectId(category_id)}, {'$set': {'income_name': income_name, 'income_category': income_category, 'income_amount': income_amount}})        
        return redirect(url_for('index'))
    
    category = income_collection.find_one({'_id': ObjectId(category_id), 'user_id': user_id})

    if category is None:
        return "Income not found or you do not have permission to edit it", 403
    
    return render_template('update_income.html', category=category)    

@app.route('/delete_income/<category_id>', methods=['POST'])
def delete_income(category_id):
    if income_collection is None:
        return "Failed to connect to the database. Please check your connection string and try again."
    
    income_collection.delete_one({'_id': ObjectId(category_id)})
    return redirect(url_for('index'))

@app.route('/add_expenses', methods=['GET', 'POST'])
def add_expenses():
    if request.method == 'POST':
        # Only allow logged in users to add income
        if 'user_id' not in session:
            return redirect(url_for('login'))

        # Retrieve the income details from form
        expenses_details = {
            "user_id": ObjectId(session['user_id']),
            "expenses_name": request.form['expenses_name'],
            "expenses_amount": float(request.form['expenses_amount'])
        }
        expenses_collection.insert_one(expenses_details)
        return redirect(url_for('index'))
    
    # For GET requests, just render the add income form
    return render_template('add_expenses.html')

@app.route('/update_expenses/<expenses_id>', methods=['GET', 'POST'])
def update_expenses(expenses_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = ObjectId(session['user_id'])
    
    if request.method == 'POST':
        category = expenses_collection.find_one({'_id': ObjectId(expenses_id), 'user_id': user_id})

        if category is None:
            return "Expenses not found or you do not have permission to edit it", 403
    
        expenses_name = request.form['expenses_name']
        expenses_amount = float(request.form['expenses_amount'])
        
        expenses_collection.update_one({'_id': ObjectId(expenses_id)}, {'$set': {'expenses_name': expenses_name, 'expenses_amount': expenses_amount}})        
        return redirect(url_for('index'))
    
    category = expenses_collection.find_one({'_id': ObjectId(expenses_id), 'user_id': user_id})

    if category is None:
        return "Expenses not found or you do not have permission to edit it", 403
    
    return render_template('update_expenses.html', category=category)    

@app.route('/delete_expenses/<expenses_id>', methods=['POST'])
def delete_expenses(expenses_id):
    if expenses_collection is None:
        return "Failed to connect to the database. Please check your connection string and try again."
    
    expenses_collection.delete_one({'_id': ObjectId(expenses_id)})
    return redirect(url_for('index'))

@app.route('/add_asset', methods=['GET', 'POST'])
def add_asset():
    if request.method == 'POST':
        # Only allow logged in users to add income
        if 'user_id' not in session:
            return redirect(url_for('login'))

        # Retrieve the income details from form
        assets_details = {
            "user_id": ObjectId(session['user_id']),
            "asset_name": request.form['asset_name'],
            "asset_amount": float(request.form['asset_amount'])
        }
        assets_collection.insert_one(assets_details)
        return redirect(url_for('index'))
    
    # For GET requests, just render the add income form
    return render_template('add_asset.html')

@app.route('/update_asset/<asset_id>', methods=['GET', 'POST'])
def update_asset(asset_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = ObjectId(session['user_id'])
    
    if request.method == 'POST':
        category = assets_collection.find_one({'_id': ObjectId(asset_id), 'user_id': user_id})

        if category is None:
            return "Assets not found or you do not have permission to edit it", 403
    
        asset_name = request.form['asset_name']
        asset_amount = float(request.form['asset_amount'])
        
        assets_collection.update_one({'_id': ObjectId(asset_id)}, {'$set': {'asset_name': asset_name, 'asset_amount': asset_amount}})        
        return redirect(url_for('index'))
    
    category = assets_collection.find_one({'_id': ObjectId(asset_id), 'user_id': user_id})

    if category is None:
        return "Assets not found or you do not have permission to edit it", 403
    
    return render_template('update_asset.html', category=category)    

@app.route('/delete_asset/<asset_id>', methods=['POST'])
def delete_asset(asset_id):
    if assets_collection is None:
        return "Failed to connect to the database. Please check your connection string and try again."
    
    assets_collection.delete_one({'_id': ObjectId(asset_id)})
    return redirect(url_for('index'))

@app.route('/add_liability', methods=['GET', 'POST'])
def add_liability():
    if request.method == 'POST':
        # Only allow logged in users to add income
        if 'user_id' not in session:
            return redirect(url_for('login'))

        # Retrieve the liability details from form
        liabilities_details = {
            "user_id": ObjectId(session['user_id']),
            "liability_name": request.form['liability_name'],
            "liability_amount": float(request.form['liability_amount'])
        }
        liabilities_collection.insert_one(liabilities_details)
        return redirect(url_for('index'))
    
    # For GET requests, just render the add income form
    return render_template('add_liability.html')

@app.route('/update_liability/<liability_id>', methods=['GET', 'POST'])
def update_liability(liability_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = ObjectId(session['user_id'])
    
    if request.method == 'POST':
        category = liabilities_collection.find_one({'_id': ObjectId(liability_id), 'user_id': user_id})

        if category is None:
            return "Liabilitty not found or you do not have permission to edit it", 403
    
        liability_name = request.form['liability_name']
        liability_amount = float(request.form['liability_amount'])
        
        liabilities_collection.update_one({'_id': ObjectId(liability_id)}, {'$set': {'liability_name': liability_name, 'liability_amount': liability_amount}})        
        return redirect(url_for('index'))
    
    category = liabilities_collection.find_one({'_id': ObjectId(liability_id), 'user_id': user_id})

    if category is None:
        return "Liabilitty not found or you do not have permission to edit it", 403
    
    return render_template('update_liability.html', category=category)    

@app.route('/delete_liability/<liability_id>', methods=['POST'])
def delete_liability(liability_id):
    if liabilities_collection is None:
        return "Failed to connect to the database. Please check your connection string and try again."
    
    liabilities_collection.delete_one({'_id': ObjectId(liability_id)})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0' ,debug=True)