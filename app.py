import os
from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy.exc import IntegrityError

from config import SECRET_KEY, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from models import (
    db,
    User,
    Expense,
    Income,
)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
db.init_app(app)

# Ensure all tables exist before handling any requests
with app.app_context():
    db.create_all()


def _extract_payload():
    """Grab data from either JSON or form so routes can read one payload style."""
    if request.is_json:
        return request.get_json(silent=True)
    if request.form:
        return request.form.to_dict()
    return None


def _to_decimal(value):
    """Turn any numeric input into a Decimal or return None when it is messy."""
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _normalize_amount(value):
    """Round money to cents so the database never stores odd precision."""
    decimal_value = _to_decimal(value)
    if decimal_value is None:
        return None
    return decimal_value.quantize(CURRENCY_QUANT)


def _clean_text(value):
    """Trim whitespace and ensure we always work with strings."""
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def _to_int(value):
    """Safely convert ids from strings to numbers."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_datetime(raw_value):
    """Convert ISO strings to datetime while falling back to now."""
    if not raw_value:
        return datetime.utcnow()
    try:
        return datetime.fromisoformat(raw_value)
    except ValueError:
        return datetime.utcnow()


def _serialize_user(user):
    """Return a plain dict copy of a user row."""
    return {
        'id': user.id,
        'firstname': user.firstname,
        'lastname': user.lastname,
        'email': user.email,
        'created_at': user.created_at.isoformat() if user.created_at else None,
    }


def _serialize_expense(record):
    """Return a plain dict copy of an expense row."""
    return {
        'id': record.id,
        'name': record.name,
        'type': record.type,
        'amount': float(record.amount),
        'currency': record.currency,
        'date': record.date.isoformat() if record.date else None,
        'user_id': record.user_id,
    }


def _serialize_income(record):
    """Return a plain dict copy of an income row."""
    return {
        'id': record.id,
        'name': record.name,
        'type': record.type,
        'amount': float(record.amount),
        'currency': record.currency,
        'frequency': record.frequency,
        'gross_net': record.gross_net,
        'date': record.date.isoformat() if record.date else None,
        'user_id': record.user_id,
    }

# Helper function to normalize all income to a monthly value
def calculate_monthly_income(income):
    """Translate different pay schedules into a monthly figure."""
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

# Home Route: Displays the landing page
@app.route('/')
def index():
    """Show the welcome page plus the list of people in the system."""
    user_data = User.query.all()
    return render_template('home.html', user_data=user_data)


# --- User CRUD API (JSON endpoints) ---
@app.route('/users', methods=['GET'])
def users_list():
    """Return every user row for API clients."""
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([_serialize_user(user) for user in users])


@app.route('/user_insert', methods=['POST'])
def user_insert():
    """Create a user record so the homepage has real people to display."""
    payload = _extract_payload()
    if not payload:
        return jsonify({'error': 'No payload supplied'}), 400

    firstname = _clean_text(payload.get('firstname') or payload.get('first_name'))
    lastname = _clean_text(payload.get('lastname') or payload.get('last_name'))
    email = _clean_text(payload.get('email'))
    password = _clean_text(payload.get('password'))

    if email:
        email = email.lower()

    if not all([firstname, lastname, email, password]):
        return jsonify({'error': 'firstname, lastname, email, and password are required'}), 400

    user = User(
        firstname=firstname,
        lastname=lastname,
        email=email,
        password=password,
    )

    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'A user with that email already exists'}), 409
    except Exception as exc:
        db.session.rollback()
        return jsonify({'error': 'Failed to create user', 'details': str(exc)}), 500

    return jsonify({
        **_serialize_user(user)
    }), 201


@app.route('/users/<int:user_id>', methods=['GET', 'PATCH', 'PUT', 'DELETE'])
def user_detail(user_id):
    """Read, update, or delete a specific user via JSON."""
    user = User.query.get_or_404(user_id)

    if request.method == 'GET':
        return jsonify(_serialize_user(user))

    if request.method in ('PATCH', 'PUT'):
        payload = _extract_payload() or {}
        pending_email = payload.get('email')

        if 'firstname' in payload:
            value = _clean_text(payload.get('firstname'))
            if value:
                user.firstname = value

        if 'lastname' in payload:
            value = _clean_text(payload.get('lastname'))
            if value:
                user.lastname = value

        if pending_email is not None:
            value = _clean_text(pending_email)
            if value:
                user.email = value.lower()

        if 'password' in payload:
            value = _clean_text(payload.get('password'))
            if value:
                user.password = value

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error': 'A user with that email already exists'}), 409
        except Exception as exc:
            db.session.rollback()
            return jsonify({'error': 'Failed to update user', 'details': str(exc)}), 500

        return jsonify(_serialize_user(user))

    # DELETE
    db.session.delete(user)
    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete user', 'details': str(exc)}), 500

    return jsonify({'success': True})


@app.route('/user_delete/<int:user_id>', methods=['GET', 'POST'])
def user_delete(user_id):
    """Remove a user along with any linked income and expense rows."""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete user', 'details': str(exc)}), 500

    if request.is_json or request.accept_mimetypes.best == 'application/json':
        return jsonify({'success': True})
    return redirect(url_for('index'))

# Dashboard Route: Displays the dashboard
@app.route('/dashboard')
def dashboard():
    """Visualize current incomes and expenses straight from Postgres."""
    expense_rows = Expense.query.order_by(Expense.date.desc()).all()
    income_rows = Income.query.order_by(Income.date.desc()).all()

    total_income_decimal = sum(calculate_monthly_income(row) for row in income_rows)
    total_income = float(total_income_decimal) if total_income_decimal else 0.0

    def _sum_expense_by(kind):
        return float(sum(row.amount for row in expense_rows if row.type == kind))

    context_expenses = [_serialize_expense(row) for row in expense_rows]
    context_incomes = [_serialize_income(row) for row in income_rows]

    return render_template('dashboard.html',
                           expenses=context_expenses,
                           incomes=context_incomes,
                           total_income=total_income,
                           total_fixed=_sum_expense_by('fixed'),
                           total_fun=_sum_expense_by('fun'),
                           total_future=_sum_expense_by('future'))

# Performance Route: Financial Performance Dashboard
@app.route('/performance')
def performance():
    """Summarize yearly income, spending, and quick coaching tips."""
    expense_rows = Expense.query.order_by(Expense.date.desc()).all()
    income_rows = Income.query.order_by(Income.date.desc()).all()

    monthly_income_decimal = sum(calculate_monthly_income(row) for row in income_rows)
    monthly_income = float(monthly_income_decimal)
    annual_income = monthly_income * 12

    total_spent_decimal = sum(row.amount for row in expense_rows)
    total_spent_so_far = float(total_spent_decimal)
    annual_expense = total_spent_so_far

    spending_tracker = {}
    for row in expense_rows:
        label = row.date.strftime("%Y-%m") if row.date else datetime.utcnow().strftime("%Y-%m")
        spending_tracker[label] = spending_tracker.get(label, 0.0) + float(row.amount)

    spending_by_month = {}
    for label in sorted(spending_tracker.keys()):
        pretty_label = datetime.strptime(label, "%Y-%m").strftime("%B %Y")
        spending_by_month[pretty_label] = spending_tracker[label]

    sorted_expenses = sorted(expense_rows, key=lambda x: x.amount, reverse=True)[:5]

    recommendations = []

    def _name_contains(keyword_list):
        for row in expense_rows:
            label = (row.name or '').lower()
            if any(keyword in label for keyword in keyword_list):
                return True
        return False

    if _name_contains(['insurance']):
        recommendations.append({
            "title": "Insurance Review",
            "text": "You have listed insurance expenses. Compare quotes with our partner <a href='#'>SafeCover</a> to potentially save up to £200/year.",
            "type": "opportunity"
        })

    if _name_contains(['energy', 'electric', 'gas', 'bill']):
         recommendations.append({
            "title": "Energy Bill Saver",
            "text": "Energy prices are fluctuating. Check if you can fix your tariff now with <a href='#'>PowerSwitch</a>.",
            "type": "opportunity"
        })

    if _name_contains(['broadband', 'internet', 'wifi']):
         recommendations.append({
            "title": "Broadband Deal",
            "text": "Is your contract ending soon? You might be overpaying for broadband. <a href='#'>NetCompare</a> has deals from £25/mo.",
            "type": "opportunity"
        })

    future_total = sum(row.amount for row in expense_rows if row.type == 'future')
    future_pct = (float(future_total) / total_spent_so_far * 100) if total_spent_so_far > 0 else 0
    if future_pct < 20:
        recommendations.append({
            "title": "Boost Your Savings",
            "text": "You are currently saving less than the recommended 20%. Try automating a transfer to a high-yield savings account on payday.",
            "type": "warning"
        })

    if monthly_income > 0 and (total_spent_so_far > monthly_income):
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
    """Handle the web form for adding real income rows."""
    users = User.query.order_by(User.firstname.asc()).all()
    error_message = None

    if request.method == 'POST':
        amount = _normalize_amount(request.form.get('amount'))
        frequency = (request.form.get('frequency') or 'monthly').lower()
        income_type = (request.form.get('income_type') or 'primary').lower()
        gross_net = (request.form.get('amount_type') or 'net').lower()
        other_description = _clean_text(request.form.get('other_description'))
        user_id = _to_int(request.form.get('user_id'))

        name = 'Primary Income' if income_type == 'primary' else (other_description or 'Other Income')

        if amount is None or user_id is None:
            error_message = 'Amount and user are required.'
        else:
            record = Income(
                name=name,
                type=income_type,
                currency='EUR',
                amount=amount,
                frequency=frequency,
                gross_net=gross_net,
                user_id=user_id,
            )

            db.session.add(record)
            try:
                db.session.commit()
                return redirect(url_for('dashboard'))
            except Exception:
                db.session.rollback()
                error_message = 'Could not save the income. Please try again.'

    return render_template('add-income.html', users=users, error_message=error_message)

# Route to add new expenses (Handles both displaying form and processing submission)
@app.route('/add-expense', methods=['GET', 'POST'])
def add_expense():
    """Handle the web form for adding real expense rows."""
    users = User.query.order_by(User.firstname.asc()).all()
    error_message = None

    if request.method == 'POST':
        description = _clean_text(request.form.get('description'))
        amount = _normalize_amount(request.form.get('amount'))
        expense_type = (request.form.get('expense_type') or 'fixed').lower()
        user_id = _to_int(request.form.get('user_id'))

        if not description or amount is None or user_id is None:
            error_message = 'Description, amount, and user are required.'
        else:
            record = Expense(
                name=description,
                currency='EUR',
                amount=amount,
                date=datetime.utcnow(),
                type=expense_type,
                user_id=user_id,
            )

            db.session.add(record)
            try:
                db.session.commit()
                return redirect(url_for('dashboard'))
            except Exception:
                db.session.rollback()
                error_message = 'Could not save the expense. Please try again.'

    return render_template('add-expense.html', users=users, error_message=error_message)


# --- Expense CRUD API (database-backed) ---
@app.route('/expenses_insert', methods=['POST'])
def expenses_insert():
    """Create a real expense row in Postgres from JSON or form data."""
    payload = _extract_payload()
    if not payload:
        return jsonify({'error': 'No payload supplied'}), 400

    name = payload.get('name') or payload.get('description')
    amount = _normalize_amount(payload.get('amount'))
    expense_type = (payload.get('type') or 'fixed').lower()
    user_id = _to_int(payload.get('user_id'))

    if not name or amount is None or user_id is None:
        return jsonify({'error': 'name, amount, and user_id are required'}), 400

    record = Expense(
        name=name,
        currency=(payload.get('currency') or 'EUR').upper(),
        amount=amount,
        date=_parse_datetime(payload.get('date')),
        type=expense_type,
        user_id=user_id,
    )

    db.session.add(record)
    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({'error': 'Failed to insert expense', 'details': str(exc)}), 500

    return jsonify(_serialize_expense(record)), 201


@app.route('/expenses', methods=['GET'])
def expenses_list():
    """Return every saved expense."""
    rows = Expense.query.order_by(Expense.date.desc()).all()
    return jsonify([_serialize_expense(row) for row in rows])


@app.route('/expenses/<int:expense_id>', methods=['GET', 'PATCH', 'PUT', 'DELETE'])
def expenses_detail(expense_id):
    """Read, change, or remove a specific expense."""
    record = Expense.query.get_or_404(expense_id)

    if request.method == 'GET':
        return jsonify(_serialize_expense(record))

    if request.method in ('PATCH', 'PUT'):
        payload = _extract_payload() or {}

        if 'name' in payload:
            value = _clean_text(payload.get('name') or payload.get('description'))
            if value:
                record.name = value

        if 'type' in payload:
            value = _clean_text(payload.get('type'))
            if value:
                record.type = value.lower()

        if 'currency' in payload:
            value = _clean_text(payload.get('currency'))
            if value:
                record.currency = value.upper()

        if 'amount' in payload:
            value = _normalize_amount(payload.get('amount'))
            if value is not None:
                record.amount = value

        if 'date' in payload:
            record.date = _parse_datetime(payload.get('date'))

        if 'user_id' in payload:
            value = _to_int(payload.get('user_id'))
            if value is not None:
                record.user_id = value

        try:
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            return jsonify({'error': 'Failed to update expense', 'details': str(exc)}), 500

        return jsonify(_serialize_expense(record))

    db.session.delete(record)
    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete expense', 'details': str(exc)}), 500

    return jsonify({'success': True})

# API Route: Delete Expense (Called via AJAX)
@app.route('/delete-expense/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """Delete an expense row from Postgres."""
    record = Expense.query.get_or_404(expense_id)
    db.session.delete(record)
    try:
        db.session.commit()
        return jsonify({'success': True})
    except Exception as exc:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(exc)}), 500

# API Route: Update Expense (Called via AJAX)
@app.route('/update-expense/<int:expense_id>', methods=['POST'])
def update_expense(expense_id):
    """Edit an expense row without leaving the dashboard."""
    record = Expense.query.get_or_404(expense_id)
    data = request.get_json(silent=True) or {}

    updates = False
    if 'description' in data or 'name' in data:
        value = _clean_text(data.get('name') or data.get('description'))
        if value:
            record.name = value
            updates = True

    if 'amount' in data:
        amount = _normalize_amount(data.get('amount'))
        if amount is None:
            return jsonify({'success': False, 'error': 'Invalid amount'}), 400
        record.amount = amount
        updates = True

    if not updates:
        return jsonify({'success': False, 'error': 'No valid fields supplied'}), 400

    try:
        db.session.commit()
        return jsonify({'success': True, 'expense': _serialize_expense(record)})
    except Exception as exc:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(exc)}), 500

# API Route: Delete Income (Called via AJAX)
@app.route('/delete-income/<int:income_id>', methods=['DELETE'])
def delete_income(income_id):
    """Remove an income entry from Postgres."""
    record = Income.query.get_or_404(income_id)
    db.session.delete(record)
    try:
        db.session.commit()
        return jsonify({'success': True})
    except Exception as exc:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(exc)}), 500

# API Route: Update Income (Called via AJAX)
@app.route('/update-income/<int:income_id>', methods=['POST'])
def update_income(income_id):
    """Edit an income entry via AJAX."""
    record = Income.query.get_or_404(income_id)
    data = request.get_json(silent=True) or {}

    updates = False
    if 'name' in data or 'description' in data or 'source' in data:
        value = _clean_text(data.get('name') or data.get('description') or data.get('source'))
        if value:
            record.name = value
            updates = True

    if 'amount' in data:
        amount = _normalize_amount(data.get('amount'))
        if amount is None:
            return jsonify({'success': False, 'error': 'Invalid amount'}), 400
        record.amount = amount
        updates = True

    if not updates:
        return jsonify({'success': False, 'error': 'No valid fields supplied'}), 400

    try:
        db.session.commit()
        return jsonify({'success': True, 'income': _serialize_income(record)})
    except Exception as exc:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(exc)}), 500


# --- Income CRUD API (database-backed) ---
@app.route('/income_insert', methods=['POST'])
def income_insert():
    """Create a real income row in Postgres from JSON or form data."""
    payload = _extract_payload()
    if not payload:
        return jsonify({'error': 'No payload supplied'}), 400

    name = payload.get('name') or payload.get('source')
    amount = _normalize_amount(payload.get('amount'))
    frequency = (payload.get('frequency') or 'monthly').lower()
    income_type = (payload.get('income_type') or payload.get('type') or 'primary').lower()
    gross_net = (payload.get('gross_net') or 'net').lower()
    user_id = _to_int(payload.get('user_id'))

    if not name or amount is None or user_id is None:
        return jsonify({'error': 'name, amount, and user_id are required'}), 400

    record = Income(
        name=name,
        type=income_type,
        currency=(payload.get('currency') or 'EUR').upper(),
        amount=amount,
        frequency=frequency,
        gross_net=gross_net,
        date=_parse_datetime(payload.get('date')),
        user_id=user_id,
    )

    db.session.add(record)
    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({'error': 'Failed to insert income', 'details': str(exc)}), 500

    return jsonify(_serialize_income(record)), 201


@app.route('/incomes', methods=['GET'])
def incomes_list():
    """Return every income row."""
    rows = Income.query.order_by(Income.date.desc()).all()
    return jsonify([_serialize_income(row) for row in rows])


@app.route('/incomes/<int:income_id>', methods=['GET', 'PATCH', 'PUT', 'DELETE'])
def incomes_detail(income_id):
    """Read, change, or remove a specific income row."""
    record = Income.query.get_or_404(income_id)

    if request.method == 'GET':
        return jsonify(_serialize_income(record))

    if request.method in ('PATCH', 'PUT'):
        payload = _extract_payload() or {}

        if 'name' in payload or 'source' in payload:
            value = _clean_text(payload.get('name') or payload.get('source'))
            if value:
                record.name = value

        if 'type' in payload or 'income_type' in payload:
            value = _clean_text(payload.get('type') or payload.get('income_type'))
            if value:
                record.type = value.lower()

        if 'currency' in payload:
            value = _clean_text(payload.get('currency'))
            if value:
                record.currency = value.upper()

        if 'amount' in payload:
            value = _normalize_amount(payload.get('amount'))
            if value is not None:
                record.amount = value

        if 'frequency' in payload:
            value = _clean_text(payload.get('frequency'))
            if value:
                record.frequency = value.lower()

        if 'gross_net' in payload:
            value = _clean_text(payload.get('gross_net'))
            if value:
                record.gross_net = value.lower()

        if 'date' in payload:
            record.date = _parse_datetime(payload.get('date'))

        if 'user_id' in payload:
            value = _to_int(payload.get('user_id'))
            if value is not None:
                record.user_id = value

        try:
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            return jsonify({'error': 'Failed to update income', 'details': str(exc)}), 500

        return jsonify(_serialize_income(record))

    db.session.delete(record)
    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete income', 'details': str(exc)}), 500

    return jsonify({'success': True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)
