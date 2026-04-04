from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Shared database helper that lets every model talk to Postgres.
db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    """Keeps each person's profile so we know who owns income and expenses."""

    id = db.Column('user_id', db.Integer, primary_key=True)
    firstname = db.Column(db.Text, nullable=False)
    lastname = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)  # Demo only – never store plain text!
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)

    expenses = db.relationship('Expense', backref='user', lazy=True, cascade='all, delete-orphan')
    incomes = db.relationship('Income', backref='user', lazy=True, cascade='all, delete-orphan')


class Expense(db.Model):
    __tablename__ = 'expenses'

    """Tracks every outgoing payment with the amount, type, and owner."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    currency = db.Column(db.Text, default='EUR', nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    frequency = db.Column(db.Text, default='monthly', nullable=False)
    date = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)
    type = db.Column(db.Text, default='fixed', nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)


class Income(db.Model):
    __tablename__ = 'incomes'

    """Stores every money-in event so we can compare it with expenses."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    type = db.Column(db.Text, nullable=False)
    currency = db.Column(db.Text, default='EUR', nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    frequency = db.Column(db.Text, default='monthly', nullable=False)
    date = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)
    gross_net = db.Column(db.Text, default='net', nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
