# My Intentional Spending Tracker

## Live Web App
- Render URL: https://intentional-spending-tracker-db.onrender.com
- Repository: https://github.com/RichieG78/intentional-spending-tracker_db.git

**Examiner test login:** Please use the following credentials to access the application.
- Username/email: `richietester@example.com`
- Password: `demo1234`

## Project Summary
My Intentional Spending Tracker is a Flask web application backed by PostgreSQL. It provides authenticated access to a budgeting dashboard where users can:
- record income and expenses,
- categorize expenses into fixed, fun, and future groups,
- set expense recurrence (weekly, fortnightly, monthly, annually),
- automatically assign new income and expense records to the logged-in user,
- edit and delete records,
- view aggregated totals and visual indicators,
- review annual performance trends.

## How to use the Intentional Spending application

Quick start (aligned to `about.html`):
1. Open the Dashboard.
2. Add your Income first (use net/take-home amount where possible).
3. Add Expenses as they occur.
4. Assign each expense to `Fixed`, `Fun`, or `Future`, and choose its recurrence.
5. Review Dashboard visuals and totals to compare actual spending vs the 50/30/20 targets.
6. Use the Performance page for annual trend review and recommendations.

**Examiner note: Please visit `/about` first. This page contains the same step-by-step usage guidance shown below and is the primary in-app instruction page. It also contains a video explaining how to use the application.**

The application design was inspired by a 50/30/20 budgeting video referenced on the About page:
- Video reference: Nischa, YouTube, 50/30/20 budgeting explainer, https://www.youtube.com/watch?v=4sT2B2SRypo

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
- Expense and Income include a frequency field to represent recurrence.
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
- 6 HTML pages with matching routes are implemented:
  - /login (login.html)
  - /about (about.html)
  - /dashboard (dashboard.html)
  - /performance (annual-performance.html)
  - /add-income (add-income.html)
  - /add-expense (add-expense.html)
- Shared navigation/layout with per-page content blocks.
- CSS styling separated under static/css/.
- JavaScript behavior separated under static/js/:
  - dashboard.js for interactive dashboard actions.
  - charts.js for chart and visual calculations.
- I intentionally did not use a generic scripts.js filename because dashboard.js and charts.js describe each JavaScript responsibility and route behavior more clearly.
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

## Deploy And Access On Render.com

Use this checklist to deploy from scratch and confirm the app is accessible.

### 1) Push code to GitHub
1. Ensure your latest code is committed and pushed.
2. Confirm the repository includes:
  - app.py
  - requirements.txt
  - templates/
  - static/

### 2) Create a PostgreSQL database on Render
1. Log in to Render.
2. Click New +, then choose PostgreSQL.
3. Set a name and region.
4. Create the database.
5. After provisioning, copy the Internal Database URL from the database dashboard.

### 3) Create the web service on Render
1. Click New +, then choose Web Service.
2. Connect your GitHub repository.
3. Configure:
  - Environment: Python
  - Build Command: pip install -r requirements.txt
  - Start Command: gunicorn app:app
4. Choose region, instance type, and branch.
5. Click Create Web Service.

### 4) Add required environment variables
In the Web Service Settings > Environment, add:
1. DATABASE_URL = the Render PostgreSQL Internal Database URL
2. SECRET_KEY = a long random value

Generate a secure SECRET_KEY locally with:
python -c "import secrets; print(secrets.token_urlsafe(48))"

Important:
- Do not wrap values in extra quotes when setting environment variables in Render.
- Do not use your local .env file in Render. Set values in the Render dashboard.

### 5) Deploy
1. Trigger a deploy from the latest commit.
2. Open the Deploy Logs and wait for a successful status.
3. Confirm you see the Gunicorn startup without fatal errors.

### 6) Access the live app
1. Open your service URL from Render (for this project: https://intentional-spending-tracker-db.onrender.com).
2. You should be able to browse public pages immediately:
  - /login
  - /about
3. Log in with a valid user account to access protected routes like /dashboard.

### 7) Verify after deployment
Run this quick smoke test:
1. Open /about and confirm page content loads.
2. Open /dashboard while logged out and confirm redirect to /login.
3. Sign in and confirm redirect to /dashboard.
4. Create one income and one expense record and confirm they display.

### 8) Common Render issues
1. 502/503 at startup:
  - Check Start Command is exactly gunicorn app:app.
2. Database errors:
  - Recheck DATABASE_URL in Render environment settings.
3. Session or auth problems:
  - Recheck SECRET_KEY is set and non-empty.
4. Missing package/module:
  - Rebuild after confirming requirements.txt includes all dependencies.

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

## UI and UX design Changes compared with previous python assignment version (Design and UI)
- Updated the visual style of the dashboard to a modern analytics-inspired design with improved spacing, color system, and card hierarchy.
- Refined layout behavior so key actions are easier to find (for example, section-level Add Expense actions for Fixed/Fun/Future).
- Replaced text-based Edit/Delete controls with icon-based action buttons using SVG assets for a cleaner card interface.
- Repositioned expense action icons to the top-right of each expense card and reduced icon size for better visual balance.
- Standardized icon button styling to use subtle borders and transparent backgrounds for a consistent look.
- Improved add-expense usability by changing expense type input to radio buttons and adding recurrence radio options.
- Improved add-income flow by removing manual user selection and assigning records automatically to the logged-in account.
- Updated app naming in shared navigation to Intentional Spending Tracker.
- To compare this new version to the previous python project you can visit that project at this git repo: https://github.com/RichieG78/MyFinancialTracker.git

## Distinction Positioning Summary
This submission targets distinction by demonstrating:
- a clear relational schema and complete CRUD coverage,
- robust Flask-to-PostgreSQL integration,
- integrated front-end behavior with modern template structure,
- secure authentication and maintainable code organization,
- a deployed, accessible, functional hosted application.

## Examiner Note on .env and Secret Key Evidence
For assessment transparency, the .env file has been added to .gitignore and is not stored in the repository history. A copy is included in the zipped folder uploaded as part of the assignment submission so the examiner can verify that environment-variable configuration was implemented, including use of SECRET_KEY in the Flask setup.


