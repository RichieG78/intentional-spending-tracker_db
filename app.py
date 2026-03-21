from flask import Flask, render_template, request, redirect, url_for, jsonify
import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/myfinancialtracker'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///myfinancialtracker_sql-test.db" # For local testing without PostgreSQL

# SQLAlchemy instance that manages ORM models and sessions
db = SQLAlchemy()
# Bind SQLAlchemy to the configured Flask app
db.init_app(app)

# Test the database connection
with app.app_context():
    try:
        db.session.execute(text("SELECT 1")) # Simple query to test DB connection
        print("Database connection successful.")
    except Exception as e:
        print(f"Database connection failed: {e}")

# --- Expense Classes ---
# Base class for all expenses
class Expense:
    def __init__(self, description, amount):
        self.id = str(uuid.uuid4()) # Unique ID for identification
        self.description = description
        self.amount = float(amount)
        self.date = datetime.now() # Record creation time
        self.type = None # To be set by subclasses

# Subclass for fixed expenses (Target: 50%)
class FixedExpense(Expense):
    def __init__(self, description, amount):
        super().__init__(description, amount)
        self.type = 'fixed'

# Subclass for fun/discretionary expenses (Target: 30%)
class FunExpense(Expense):
    def __init__(self, description, amount):
        super().__init__(description, amount)
        self.type = 'fun'

# Subclass for savings/future expenses (Target: 20%)
class FutureExpense(Expense):
    def __init__(self, description, amount):
        super().__init__(description, amount)
        self.type = 'future'

# --- Income Classes ---
# Base class for income sources
class Income:
    def __init__(self, amount, frequency):
        self.id = str(uuid.uuid4()) # Unique ID for identification
        self.amount = float(amount)
        self.frequency = frequency
        self.description = None
        self.type = None

# Subclass for the main salary/primary income
class PrimaryIncome(Income):
    def __init__(self, amount, frequency):
        super().__init__(amount, frequency)
        self.description = "Primary Income"
        self.type = 'primary'

# Subclass for any additional income sources
class OtherIncome(Income):
    def __init__(self, amount, frequency, description=None):
        super().__init__(amount, frequency)
        self.type = 'other'
        if description:
            self.description = description
        else:
             self.description = "Other Income"

# In-memory storage (reset on server restart)
expenses = []
incomes = []

# Helper function to normalize all income to a monthly value
def calculate_monthly_income(income):
    amount = income.amount
    freq = income.frequency.lower()
    if freq == 'hourly':
        return amount * 40 * 52 / 12 # Approximation: 40hr work week
    elif freq == 'weekly':
        return amount * 52 / 12
    elif freq == 'monthly':
        return amount
    elif freq == 'annually':
        return amount / 12
    return 0

# --- Routes ---

from sqlalchemy import text 
# Home Route: Displays the landing page
@app.route('/')
def index():
    db.session.execute(text("CREATE TABLE IF NOT EXISTS user( id INT, username TEXT)")) # Simple query to test DB connection
    return render_template('home.html')

# Dashboard Route: Displays the dashboard
@app.route('/dashboard')
def dashboard():
    # Calculate totals for charts
    total_income = sum(calculate_monthly_income(i) for i in incomes)
    total_fixed = sum(e.amount for e in expenses if e.type == 'fixed')
    total_fun = sum(e.amount for e in expenses if e.type == 'fun')
    total_future = sum(e.amount for e in expenses if e.type == 'future')

    return render_template('dashboard.html', 
                           expenses=expenses, 
                           incomes=incomes,
                           total_income=total_income,
                           total_fixed=total_fixed,
                           total_fun=total_fun,
                           total_future=total_future)

# Performance Route: Financial Performance Dashboard
@app.route('/performance')
def performance():
    # 1. Annual Calculation
    monthly_income = sum(calculate_monthly_income(i) for i in incomes)
    annual_income = monthly_income * 12
    
    # Calculate total money spent so far (Simple sum of all recorded expenses)
    total_spent_so_far = sum(e.amount for e in expenses)
    
    # Simple projection: Annual expense = average daily expense * 365 
    # (Just for demo purposes, or just use sum if we assume data is comprehensive)
    annual_expense = total_spent_so_far # In a real app this would be more complex

    # 2. Monthly Breakdown (Mocking dates for demonstration if needed, or using actuals)
    spending_by_month = {}
    for e in expenses:
        month_key = e.date.strftime("%B %Y")
        spending_by_month[month_key] = spending_by_month.get(month_key, 0) + e.amount

    # 3. Top Spending Categories/Items
    sorted_expenses = sorted(expenses, key=lambda x: x.amount, reverse=True)[:5]
    
    # 4. Recommendations Logic
    recommendations = []
    
    # Insurance Check
    if any("insurance" in e.description.lower() for e in expenses):
        recommendations.append({
            "title": "Insurance Review",
            "text": "You have listed insurance expenses. Compare quotes with our partner <a href='#'>SafeCover</a> to potentially save up to £200/year.",
            "type": "opportunity"
        })
    
    # Energy/Bills Check
    if any(k in e.description.lower() for k in ['energy', 'electric', 'gas', 'bill'] for e in expenses):
         recommendations.append({
            "title": "Energy Bill Saver",
            "text": "Energy prices are fluctuating. Check if you can fix your tariff now with <a href='#'>PowerSwitch</a>.",
            "type": "opportunity"
        })

    # Broadband Check
    if any(k in e.description.lower() for k in ['broadband', 'internet', 'wifi'] for e in expenses):
         recommendations.append({
            "title": "Broadband Deal",
            "text": "Is your contract ending soon? You might be overpaying for broadband. <a href='#'>NetCompare</a> has deals from £25/mo.",
            "type": "opportunity"
        })

    # Saving Check (Future Fund)
    future_pct = (sum(e.amount for e in expenses if e.type == 'future') / total_spent_so_far) * 100 if total_spent_so_far > 0 else 0
    if future_pct < 20:
        recommendations.append({
            "title": "Boost Your Savings",
            "text": "You are currently saving less than the recommended 20%. Try automating a transfer to a high-yield savings account on payday.",
            "type": "warning"
        })

    # Generic high spending
    if monthly_income > 0 and (total_spent_so_far > monthly_income): # Comparing total spend vs 1 month income is tough without time window, simplified for now
         recommendations.append({
            "title": "High Expenditure Alert",
            "text": "Your recorded expenses exceed your monthly income. Review your 'Fun' category for quick wins.",
            "type": "alert"
        })

    return render_template('annual-performance.html',
                           annual_income=annual_income,
                           annual_expense=annual_expense,
                           spending_by_month=spending_by_month,
                           top_expenses=sorted_expenses,
                           recommendations=recommendations)

# Route to add new income (Handles both displaying form and processing submission)
@app.route('/add-income', methods=['GET', 'POST'])
def add_income():
    if request.method == 'POST':
        amount = request.form.get('amount')
        frequency = request.form.get('frequency')
        income_type = request.form.get('income_type')
        other_description = request.form.get('other_description')

        if amount and frequency and income_type:
            new_income = None
            if income_type == 'primary':
                new_income = PrimaryIncome(amount, frequency)
            elif income_type == 'other':
                # Use provided description or generate a default like "Other 1", "Other 2"
                if not other_description:
                    count = len([i for i in incomes if i.type == 'other']) + 1
                    other_description = f"Other Income {count}"
                new_income = OtherIncome(amount, frequency, other_description)
            
            if new_income:
                incomes.append(new_income)
                return redirect(url_for('dashboard'))

    return render_template('add-income.html')

# Route to add new expenses (Handles both displaying form and processing submission)
@app.route('/add-expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        description = request.form.get('description')
        amount = request.form.get('amount')
        expense_type = request.form.get('expense_type')
        
        if description and amount and expense_type:
            new_expense = None
            # Instantiate correct class based on user selection
            if expense_type == 'fixed':
                new_expense = FixedExpense(description, amount)
            elif expense_type == 'fun':
                new_expense = FunExpense(description, amount)
            elif expense_type == 'future':
                new_expense = FutureExpense(description, amount)
            
            if new_expense:
                expenses.append(new_expense)
                return redirect(url_for('dashboard'))
            
    return render_template('add-expense.html')

# API Route: Delete Expense (Called via AJAX)
@app.route('/delete-expense/<expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    global expenses
    initial_count = len(expenses)
    # Filter out the expense with the matching ID
    expenses = [e for e in expenses if e.id != expense_id]
    
    if len(expenses) < initial_count:
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Expense not found'}), 404

# API Route: Update Expense (Called via AJAX)
@app.route('/update-expense/<expense_id>', methods=['POST'])
def update_expense(expense_id):
    data = request.json
    for expense in expenses:
        if expense.id == expense_id:
            if 'description' in data:
                expense.description = data['description']
            if 'amount' in data:
                try:
                    expense.amount = float(data['amount'])
                except ValueError:
                    return jsonify({'success': False, 'error': 'Invalid amount'}), 400
            return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Expense not found'}), 404

# API Route: Delete Income (Called via AJAX)
@app.route('/delete-income/<income_id>', methods=['DELETE'])
def delete_income(income_id):
    global incomes
    initial_count = len(incomes)
    incomes = [i for i in incomes if i.id != income_id]
    if len(incomes) < initial_count:
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Income not found'}), 404

# API Route: Update Income (Called via AJAX)
@app.route('/update-income/<income_id>', methods=['POST'])
def update_income(income_id):
    data = request.json
    for income in incomes:
        if income.id == income_id:
            if 'description' in data:
                income.description = data['description']
            if 'amount' in data:
                try:
                    income.amount = float(data['amount'])
                except ValueError:
                    return jsonify({'success': False, 'error': 'Invalid amount'}), 400
            return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Income not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
