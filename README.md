# My Financial Tracker

## Live Web App
- Render URL: https://myfinancialtracker.onrender.com/
- Repository: https://github.com/RichieG78/MyFinancialTracker.git

## Project Summary
My Financial Tracker is a Flask web application backed by PostgreSQL. It provides authenticated access to a budgeting dashboard where users can:
- record income and expenses,
- categorize expenses into fixed, fun, and future groups,
- edit and delete records,
- view aggregated totals and visual indicators,
- review annual performance trends.

The implementation is aligned to the Module 4 Databases assignment brief and rubric in 4_Databases_Assignment.pdf.

## Assignment Requirements Mapping (Distinction-Focused)

### 1) Database Schema and CRUD Logic
Distinction criterion: strong application of schema and CRUD concepts.

Evidence in this project:
- Relational schema defined with SQLAlchemy models in models.py:
  - User
  - Expense
  - Income
- Primary and foreign keys implemented:
  - User.id is the parent key.
  - Expense.user_id and Income.user_id reference User.
- Full CRUD routes implemented for core entities:
  - Users: create/list/detail update/delete
  - Expenses: create/list/detail update/delete
  - Incomes: create/list/detail update/delete
- HTTP methods used meaningfully:
  - GET for retrieval
  - POST for creation and selected update handlers
  - PATCH/PUT for partial/full updates
  - DELETE for deletion

### 2) Flask + PostgreSQL Integration
Distinction criterion: strong ability to apply DB integration in Flask.

Evidence in this project:
- Flask-SQLAlchemy configured via environment variables in config.py:
  - SQLALCHEMY_DATABASE_URI from DATABASE_URL
- PostgreSQL used in both local and hosted setup.
- Database objects are initialized and tables created inside app context.
- Render-hosted PostgreSQL connection is used for deployed runtime.

### 3) Modern HTML/CSS/JavaScript Integration
Distinction criterion: strong frontend integration with modern styling and interaction.

Evidence in this project:
- Multiple templates with Jinja2 inheritance via templates/base.html.
- Shared navigation/layout with per-page content blocks.
- CSS styling separated under static/css/.
- JavaScript behavior separated under static/js/:
  - dashboard.js for interactive dashboard actions.
  - charts.js for chart and visual calculations.
- UI includes dynamic updates, category totals, and visual budget feedback.

### 4) Clean Code Structure and Best Practice
Distinction criterion: strong clean structure, organization, and best practice.

Evidence in this project:
- Separation of concerns:
  - app.py for routes and orchestration
  - models.py for schema
  - utils.py for parsing/normalization/serialization helpers
  - templates/ for presentation
  - static/ for CSS and JS
- Reusable base template reduces duplication and improves maintainability.
- Password security implemented:
  - hashed passwords using Werkzeug (pbkdf2:sha256)
  - login verification via hash checking
- Flask-Login integrated for session-based authentication and route protection.
- Sensitive debug exposure removed from templates.

### 5) Hosted, Accessible, Functional Web App
Distinction criterion: strong evidence of hosted app functionality and accessibility.

Evidence in this project:
- Application deployed on Render and publicly accessible.
- Uses gunicorn start command and environment-based configuration.
- Core routes and auth flow run in hosted environment.

## Technical Stack
- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- PostgreSQL
- HTML + Jinja2
- CSS
- JavaScript
- Gunicorn (deployment)

## Route Overview
- Public/auth:
  - /login
  - /logout
  - /about
- App pages:
  - /dashboard
  - /performance
  - /add-income
  - /add-expense
- User API:
  - /users
  - /users/<user_id>
  - /user_insert
  - /user_delete/<user_id>
- Expense API:
  - /expenses
  - /expenses/<expense_id>
  - /expenses_insert
  - /delete-expense/<expense_id>
  - /update-expense/<expense_id>
- Income API:
  - /incomes
  - /incomes/<income_id>
  - /income_insert
  - /delete-income/<income_id>
  - /update-income/<income_id>

## Local Run Instructions
1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:
   - pip install -r requirements.txt
4. Set environment variables in .env:
   - DATABASE_URL=<your_postgres_connection_string>
   - SECRET_KEY=<your_secret_key>
5. Run:
   - python3 app.py
6. Open:
   - http://127.0.0.1:5000

## Render Deployment Notes
- Build command:
  - pip install -r requirements.txt
- Start command:
  - gunicorn app:app
- Required environment variables:
  - DATABASE_URL
  - SECRET_KEY

## Dependencies
Defined in requirements.txt:
- Flask
- Flask-SQLAlchemy
- Flask-Login
- psycopg2-binary
- python-dotenv
- gunicorn

## Distinction Positioning Summary
This submission targets distinction by demonstrating:
- a clear relational schema and complete CRUD coverage,
- robust Flask-to-PostgreSQL integration,
- integrated front-end behavior with modern template structure,
- secure authentication and maintainable code organization,
- a deployed, accessible, functional hosted application.

## Assignment Reference
- 4_Databases_Assignment.pdf (project folder)
