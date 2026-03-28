import uuid
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.Text, nullable=False)
    lastname = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)  # Demo only – never store plain text!
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)

    expenses = db.relationship('Expense', backref='user', lazy=True, cascade='all, delete-orphan')
    incomes = db.relationship('Income', backref='user', lazy=True, cascade='all, delete-orphan')


class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    currency = db.Column(db.Text, default='EUR', nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    date = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)
    type = db.Column(db.Text, default='fixed', nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class Income(db.Model):
    __tablename__ = 'incomes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    type = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    frequency = db.Column(db.Text, default='monthly', nullable=False)
    date = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)
    gross_net = db.Column(db.Text, default='net', nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


# --- In-memory helper classes used by the dashboard demo ---
class _DemoExpense:
    def __init__(self, description, amount):
        self.id = str(uuid.uuid4())
        self.description = description
        self.amount = float(amount)
        self.currency = 'EUR'
        self.date = datetime.utcnow()


class FixedExpense(_DemoExpense):
    def __init__(self, description, amount):
        super().__init__(description, amount)
        self.type = 'fixed'


class FunExpense(_DemoExpense):
    def __init__(self, description, amount):
        super().__init__(description, amount)
        self.type = 'fun'


class FutureExpense(_DemoExpense):
    def __init__(self, description, amount):
        super().__init__(description, amount)
        self.type = 'future'


class _DemoIncome:
    def __init__(self, amount, frequency, description):
        self.id = str(uuid.uuid4())
        self.description = description
        self.amount = float(amount)
        self.frequency = frequency
        self.type = 'primary'
        self.currency = 'EUR'
        self.created_at = datetime.utcnow()


class PrimaryIncome(_DemoIncome):
    def __init__(self, amount, frequency):
        super().__init__(amount, frequency, "Primary Income")
        self.type = 'primary'


class OtherIncome(_DemoIncome):
    def __init__(self, amount, frequency, description=None):
        label = description if description else "Other Income"
        super().__init__(amount, frequency, label)
        self.type = 'other'


# In-memory storage leveraged by dashboard visualisations
expenses = []
incomes = []
