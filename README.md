# My Financial Tracker

## Live Web App
- Render URL: https://myfinancialtracker.onrender.com/
- Repository: https://github.com/RichieG78/intentional-spending-tracker_db.git

**Examiner test login:** Please use the following credentials to access the application.
- Username/email: `richietester@example.com`
- Password: `demo1234`

## Project Summary
My Financial Tracker is a Flask web application backed by PostgreSQL. It provides authenticated access to a budgeting dashboard where users can:
- record income and expenses,
- categorize expenses into fixed, fun, and future groups,
- edit and delete records,
- view aggregated totals and visual indicators,
- review annual performance trends.

## How to user the Intentional spender applaction

**Examiner note: Please visit `/about` first. This page contains the same step-by-step usage guidance shown below and is the primary in-app instruction page.**

Quick start (aligned to `about.html`):
1. Open the Dashboard.
2. Add your Income first (use net/take-home amount where possible).
3. Add Expenses as they occur.
4. Assign each expense to `Fixed`, `Fun`, or `Future`.
5. Review Dashboard visuals and totals to compare actual spending vs the 50/30/20 targets.
6. Use the Performance page for annual trend review and recommendations.

The application design was inspired by the 50/30/20 budgeting video embedded on the About page:
- https://www.youtube.com/embed/4sT2B2SRypo

That video influenced the structure of the app by shaping:
- the use of the 50/30/20 budgeting model,
- the separation of spending into Fixed, Fun, and Future categories,
- the educational About page that explains the budgeting method before use,
- and the dashboard layout that helps users compare actual spending against target percentages.

## Assignment Requirements (Distinction-Focused)

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
Distinction criteria: Evidence of strong ability to apply database integration in Flask:
- Flask-SQLAlchemy configured via environment variables in config.py:
  - SQLALCHEMY_DATABASE_URI from DATABASE_URL
- PostgreSQL used in both local and hosted setup.
- Database objects are initialized and tables created inside app context.
- Render-hosted PostgreSQL connection is used for deployed runtime.

### 3) Modern HTML/CSS/JavaScript Integration
Distinction criteria: frontend integration with modern styling and interaction.

Evidence in this project:
- Multiple templates with Jinja2 inheritance via templates/base.html.
- Shared navigation/layout with per-page content blocks.
- CSS styling separated under static/css/.
- JavaScript behavior separated under static/js/:
  - dashboard.js for interactive dashboard actions.
  - charts.js for chart and visual calculations.
- UI includes dynamic updates, category totals, and visual budget feedback.

### 4) Clean Code Structure and Best Practice
Distinction critera: strong clean structure, organization, and best practice.

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
Distinction criteria: strong evidence of hosted app functionality and accessibility.

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

## Automated Testing
This project includes automated tests using Flask's built-in test client.

Test file:
- test_app.py

Current coverage includes:
- route rendering check (about page returns 200)
- authentication protection check (dashboard redirects to login when not signed in)
- POST creation check (user_insert creates a database record)
- login flow check (valid credentials redirect to dashboard)

Run tests locally:
1. Activate the virtual environment.
2. Run: python -m unittest -v test_app.py

Expected result:
- 4 tests run, all passing.

## Distinction Positioning Summary
This submission targets distinction by demonstrating:
- a clear relational schema and complete CRUD coverage,
- robust Flask-to-PostgreSQL integration,
- integrated front-end behavior with modern template structure,
- secure authentication and maintainable code organization,
- a deployed, accessible, functional hosted application.

## Examiner Note on .env and Secret Key Evidence
For assessment transparency, I am intentionally keeping the .env file available in this repository and visible in git history so the examiner can verify that environment-variable configuration was implemented, including use of SECRET_KEY in the Flask setup.


