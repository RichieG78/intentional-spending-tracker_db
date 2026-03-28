import uuid
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, Text, TIMESTAMP

db = SQLAlchemy()												

class User(db.Model):
    user_id     = db.Column(db.Integer, primary_key=True)
    firstname   = db.Column(db.Text, nullable=False)
    lastname    = db.Column(db.Text, nullable=False)
    email       = db.Column(db.Text, unique=True, nullable=False)
	##WARNING: SECURITY: Do NOT store a password like this: just for play here
    password    = db.Column(db.Text, nullable=False)
    created_at  = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)

# --- Expense Classes ---
# Base class for all expenses
class Expense(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.Text, nullable=False)
    currency    = db.Column(db.Text, default='EUR', nullable=False)
    amount      = db.Column(db.Float, nullable=False)
    date        = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)
    type        = db.Column(db.Text, nullable=False)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

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
