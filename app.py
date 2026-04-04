import os
from datetime import datetime
from urllib.parse import urljoin, urlparse

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from config import SECRET_KEY, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from models import (
    db,
    User,
    Expense,
    Income,
)
from utils import (
    _extract_payload,
    _normalize_amount,
    _clean_text,
    _to_int,
    _parse_datetime,
    _serialize_user,
    _serialize_expense,
    _serialize_income,
    calculate_monthly_income,
)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Please sign in to continue.'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    """Reloads a person from the session-stored user id."""
    if not user_id:
        return None
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None


def _is_safe_next_url(target):
    """Only allow redirects that stay on this site."""
    if not target:
        return False
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return redirect_url.scheme in ('http', 'https') and host_url.netloc == redirect_url.netloc


def _password_is_hashed(password_value):
    return isinstance(password_value, str) and password_value.startswith(('pbkdf2:', 'scrypt:'))


def _hash_password(raw_password):
    # Force pbkdf2 for compatibility with Python builds that do not support scrypt.
    return generate_password_hash(raw_password, method='pbkdf2:sha256')


def _password_matches(stored_password, plain_password):
    if not stored_password or not plain_password:
        return False
    if _password_is_hashed(stored_password):
        return check_password_hash(stored_password, plain_password)
    return stored_password == plain_password

# Ensure all tables exist before handling any requests
with app.app_context():
    db.create_all()

# --- Routes ---

# Login / Logout Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Shows the sign-in form and checks the email/password against the database."""
    # If already logged in, skip straight to the dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    error_message = None
    next_url = request.args.get('next')

    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        password = (request.form.get('password') or '').strip()

        # Look up the person by email
        user = User.query.filter_by(email=email).first()

        # Check hashed passwords (with one-time fallback for legacy plain-text rows).
        if user and _password_matches(user.password, password):
            if not _password_is_hashed(user.password):
                user.password = _hash_password(password)
                db.session.commit()
            login_user(user)

            next_url = (request.form.get('next') or next_url or '').strip()
            if next_url and _is_safe_next_url(next_url):
                return redirect(next_url)
            return redirect(url_for('dashboard'))

        error_message = 'Incorrect email or password. Please try again.'

    return render_template('login.html', error_message=error_message, next_url=next_url)


@app.route('/logout')
@login_required
def logout():
    """Clears the session and sends the person back to the login page."""
    logout_user()
    return redirect(url_for('login'))


# Home Route: Displays the landing page
@app.route('/')
def index():
    """Redirects to the main dashboard page."""
    return redirect(url_for('dashboard'))


@app.route('/about')
def about():
    """Shows the about page with app background and budgeting guidance."""
    user_data = User.query.all()
    return render_template('about.html', user_data=user_data)


# --- User CRUD API (JSON endpoints): small helpers that add, list, edit, or remove people ---
@app.route('/users', methods=['GET'])
def users_list():
    """Reads every person from the database, newest first, and hands back simple data about them."""
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([_serialize_user(user) for user in users])


@app.route('/user_insert', methods=['POST'])
def user_insert():
    """Creates a brand-new person so the rest of the app has someone to link to."""
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
        password=_hash_password(password),
    )

    db.session.add(user)
    # Try to lock the new person into the database, and give a friendly error if it fails
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
    """Lets us peek at, tweak, or remove a single person."""
    # Grab the requested person (or send a 404 if they are missing)
    user = User.query.get_or_404(user_id)

    # READ: if someone just wants to see the person, return the basics right away
    if request.method == 'GET':
        return jsonify(_serialize_user(user))

    # UPDATE: PATCH/PUT calls want to change specific fields sent in the payload
    if request.method in ('PATCH', 'PUT'):
        payload = _extract_payload() or {}
        pending_email = payload.get('email')

        # Adjust the first name when a new value was supplied
        if 'firstname' in payload:
            value = _clean_text(payload.get('firstname'))
            if value:
                user.firstname = value

        # Adjust the last name when a new value was supplied
        if 'lastname' in payload:
            value = _clean_text(payload.get('lastname'))
            if value:
                user.lastname = value

        # Email gets lowercased so duplicates are easier to spot
        if pending_email is not None:
            value = _clean_text(pending_email)
            if value:
                user.email = value.lower()

        # Update passwords only if a non-empty value came through
        if 'password' in payload:
            value = _clean_text(payload.get('password'))
            if value:
                user.password = _hash_password(value)

        # Try to save the edits, surfacing friendly errors on conflicts
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
    # REMOVE: wipe the person entirely when DELETE is called
    db.session.delete(user)
    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete user', 'details': str(exc)}), 500

    return jsonify({'success': True})


@app.route('/user_delete/<int:user_id>', methods=['GET', 'POST'])
def user_delete(user_id):
    """Removes someone and all of their money records in one go."""
    # Look up the person using the id from the URL; send a 404 if it is bogus
    user = User.query.get_or_404(user_id)
    # Remove the person plus their related expense/income rows in one transaction
    db.session.delete(user)
    try:
        # Try to save the deletion and roll back if anything fails
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete user', 'details': str(exc)}), 500

    # If the caller wanted JSON (AJAX), send a JSON success response
    if request.is_json or request.accept_mimetypes.best == 'application/json':
        return jsonify({'success': True})
    # Otherwise bounce a browser user back to the home page so the list refreshes
    return redirect(url_for('index'))

# Dashboard Route: Displays the dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    """Shows a friendly overview of how money is coming in and going out."""
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
@login_required
def performance():
    """Tells a simple story about how the year looks plus a few tips."""
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
            "text": "You have listed insurance expenses. Compare quotes with our partner <a href='#'>SafeCover</a> to potentially save up to €200/year.",
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
            "text": "Is your contract ending soon? You might be overpaying for broadband. <a href='#'>NetCompare</a> has deals from €25/mo.",
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
@login_required
def add_income():
    """Shows the add-income form and saves the entry when it is submitted."""
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
@login_required
def add_expense():
    """Shows the add-expense form and stores the purchase once submitted."""
    error_message = None
    allowed_types = {'fixed', 'fun', 'future'}
    selected_expense_type = (request.args.get('expense_type') or 'fixed').strip().lower()
    if selected_expense_type not in allowed_types:
        selected_expense_type = 'fixed'

    if request.method == 'POST':
        description = _clean_text(request.form.get('description'))
        amount = _normalize_amount(request.form.get('amount'))
        expense_type = (request.form.get('expense_type') or selected_expense_type).lower()
        if expense_type not in allowed_types:
            expense_type = 'fixed'
        selected_expense_type = expense_type
        user_id = current_user.id

        if not description or amount is None:
            error_message = 'Description and amount are required.'
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

    return render_template(
        'add-expense.html',
        error_message=error_message,
        selected_expense_type=selected_expense_type,
    )


# --- Expense CRUD API (database-backed) ---
@app.route('/expenses_insert', methods=['POST'])
def expenses_insert():
    """Adds a new expense to the database using whatever data the caller sends."""
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
    """Lists every expense we have on file."""
    rows = Expense.query.order_by(Expense.date.desc()).all()
    return jsonify([_serialize_expense(row) for row in rows])


@app.route('/expenses/<int:expense_id>', methods=['GET', 'PATCH', 'PUT', 'DELETE'])
def expenses_detail(expense_id):
    """Looks at one expense and lets callers update or delete it."""
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
    """Removes an expense right away when someone clicks delete on the dashboard."""
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
    """Lets the dashboard inline editor rename a purchase or change its amount."""
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
    """Removes an income entry when someone deletes it from the UI."""
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
    """Lets the dashboard inline editor rename or resize an income entry."""
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
    """Adds a new income row in the database from either JSON or form data."""
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
    """Lists every income entry on record."""
    rows = Income.query.order_by(Income.date.desc()).all()
    return jsonify([_serialize_income(row) for row in rows])


@app.route('/incomes/<int:income_id>', methods=['GET', 'PATCH', 'PUT', 'DELETE'])
def incomes_detail(income_id):
    """Looks at one income entry and lets callers update or delete it."""
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
