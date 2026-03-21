# Intentional Spending Tracker

[GitHub Repository] https://github.com/RichieG78/MyFinancialTracker.git

## Website

**[View Intentional Spending Tracker Live](https://myfinancialtracker.onrender.com/)**

---

## Project Goal
The Intentional Spending Tracker is a personal finance web application built using **Python and Flask**, designed to help users better understand and control their spending by comparing **intended spending goals** against **actual financial behaviour**.

The core concept of the application is based on an intentional budgeting framework, where all spending is categorised into three clearly defined sections:

- **Fixed (50%)** – essential and recurring expenses such as rent, bills, and groceries
- **Fun (30%)** – discretionary spending such as entertainment, dining, and hobbies
- **Future (20%)** – savings, investments, and long-term financial planning

The application allows users to record income and expenses, automatically calculate how spending is distributed across these categories, and visually compare the **target percentages** against the **actual percentages** being spent.

The project was created specifically to demonstrate a strong understanding of **Flask application structure**, **object-oriented Python**, and the **integration of HTML, CSS, and JavaScript** in line with the Python assignment brief.

---

## Installation and Execution

To run the application locally for development or assessment purposes:

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/RichieG78/MyFinancialTracker.git
    cd MyFinancialTracker
    ```

2.  **Create and Activate Virtual Environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On macOS/Linux
    # venv\Scripts\activate   # On Windows
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Application**
    ```bash
    python3 app.py
    ```
    The application will be accessible at `http://127.0.0.1:5000/`.

---

## 1. Project Conceptualisation and Planning

### 1.1 Project Concept
The Intentional Spending Tracker was designed to move beyond a basic expense tracker and instead focus on **behavioural insight**. By framing financial data around intention versus reality, the application helps users quickly identify where their spending habits align with, or diverge from, their financial goals.

Key features include:
- Income tracking with automatic frequency calculation
- Expense tracking
- Three-category intentional spending model (Fixed / Fun / Future)
- Automatic calculation of spending percentages
- Visual comparison of target versus actual spending
- **Real-time budget health notifications** (warnings when overspending, success message when budget is balanced)
- **Educational Home Page** with embedded video guide and clear instructions
- **Financial Performance Dashboard**: Annualized view with spending trends and intelligent savings recommendations (Original feature).
- Dashboard-style single-page overview

This concept directly aligns with the assignment requirement to build a **functional, engaging, and visually appealing web application** using Flask.
, Research & Inspiration
Prior to development, research was conducted into personal finance dashboards and budgeting methodologies.

**Inspiration:**
The core **50/30/20 framework** and the specific **interactive dashboard design** were inspired by the financial educator **Nischa** and her video guide on the topic (embedded on the Home page and link here: https://youtu.be/4sT2B2SRypo). The visual concept of separating expenses into three distinct buckets for immediate visual feedback and the initial design of the dashboard page is drawn directly from her google spreadsheet design and her advice.

**Original Contributions:**
While the dashboard follows this inspired structure, all other features are original implementations created for this project, including:
- The **Financial Performance** dashboard logic and design.
- The **smart recommendation system** suggesting savings on insurance and utilities.
- The **backend logic** for annualized projections and health-check notifications.
- Goal tracking interfaces

This research influenced several design decisions, including:
- Using a **three-column dashboard layout** inspired by Kanban boards to represent the Fixed, Fun, and Future categories
- Presenting spending items as cards within each column
- Using progress bars and percentage indicators to visualise financial goals

These design choices ensured that the application would be intuitive, visually clear, and suitable for a single-page dashboard layout.

### 1.3 Sitemap and Wireframes
The application uses a small number of focused routes built in html and demonstrating flash and Jinja integration:
- Home
- Dashboard
- Add Income
- Add Expense
- Performance

Wireframes were created to plan the three-column dashboard layout and ensure consistent placement of totals, progress indicators, and transaction cards across screen sizes.

---

## 2. Flask Application Structure

### 2.1 Flask Setup
The application was built using Flask following the setup process outlined in the assignment brief:
- Flask installed using `pip`
- Virtual environment created and activated
- Application entry point defined in `app.py`

Flask is responsible for:
- Routing
- Rendering templates
- Handling GET, POST, DELETE and PUT requests
- Passing processed data to the front-end

### 2.2 Routes
The following routes are implemented:

- `/` – Landing page with educational content and budget framework guide
- `/dashboard` – Main dashboard displaying spending overview, charts and expense lists
- `/performance` – Financial Performance dashboard with spending trends and recommendations
- `/add-income` – Form to add income entries (GET/POST)
- `/add-expense` – Form to add spending transactions (GET/POST)
- `/delete-expense/<expense_id>` – API endpoint to delete an expense (DELETE)
- `/update-expense/<expense_id>` – API endpoint to update an expense description or amount (POST)
- `/delete-income/<income_id>` – API endpoint to delete an income source (DELETE)
- `/update-income/<income_id>` – API endpoint to update an income description or amount (POST)

These routes demonstrate the use of multiple HTTP methods (`GET`, `POST`, `DELETE`) and Flask’s `render_template` and `jsonify` functionality.

---

## 3. Python Programming and Class Design

### 3.1 Object-Oriented Design
The application uses **multiple custom Python classes** with inheritance to model real-world financial concepts, demonstrating strong understanding of Python programming principles:

- `Income` (Base Class)
    - `PrimaryIncome` – Represents main salary or wages
    - `OtherIncome` – Represents secondary or irregular income sources
- `Expense` (Base Class)
    - `FixedExpense` – Represents essential spending (50% target)
    - `FunExpense` – Represents discretionary spending (30% target)
    - `FutureExpense` – Represents savings and investments (20% target)

This class-based approach improves code readability, separation of concerns, and scalability.

### 3.2 Data Processing
All financial calculations are handled in Python, including:
- Total income calculation (converting different frequencies to monthly)
- Total spending per category
- **In-memory data storage:** For the scope of this assignment, data is stored in global lists (`expenses` and `incomes`). This ensures simple deployment and focuses the project on Python logic and Flask structure. Use of a persistent database (SQLite/PostgreSQL) would be a future enhancement.

Only processed data is passed to the templates, ensuring that presentation logic remains separate from business logic.

---

## 4. HTML Structure and Content

### 4.1 Templates
The application includes **five distinct HTML templates**, successfully meeting the assignment requirement for multiple page structures. Each template shares a consistent design while serving a unique purpose:

- `home.html` – The landing page, featuring an **embedded educational video** and clear breakdown of the 50/30/20 framework.
- `dashboard.html` – The main interface showing charts, transaction columns, and the **budget countdown counter** for real-time feedback.
- `annual-performance.html` – A detailed report page showing annualized spending projections and intelligent financial recommendations.
- `add-income.html` – A dedicated form page for adding and calculating income sources.
- `add-expense.html` – A dedicated form page for recording new transactions.

Each template includes semantic HTML elements such as `<header>`, `<main>`, and `<nav>` to improve accessibility and maintainability.

### 4.2 Dashboard Layout
The main dashboard is divided into two key sections:

**1. Overview & Visuals (Top Row):**
- **Income Summary:** Displays total income, total expenses, and remaining budget with status alerts.
- **Expenditure Charts:** Visual progress bars comparing **Target** vs **Actual** percentages for each category.

**2. Expense Tracker (Bottom Row):**
A **three-column layout** where each column represents one spending category (Fixed, Fun, Future) and displays:
- Category Header
- List of individual transaction cards (with edit/delete options)
- Total category spend summary

---

## 5. CSS Styling

### 5.1 Visual Design
Modern CSS is used to create a clean, professional dashboard aesthetic:
- Card-based UI components
- Consistent spacing and typography
- Category-specific colour accents

### 5.2 Layout Techniques
The layout is implemented using:
- **CSS Grid** for the three-column dashboard
- **Flexbox** for card and form alignment

### 5.3 Desktop-First Design Approach
The application is explicitly designed for **desktop use**. Mobile responsiveness was not a stated requirement for this assignment, and a deliberate design decision was made to prioritize the desktop experience. The complex 3-column dashboard layout is optimized for wider screens (1280px+) to allow users to view their entire financial picture—goals, actuals, and transactions—at a single glance, aligning with the typical user behavior of managing detailed finances on a computer. Use on mobile devices is not supported in this version, but could be developed for later versions.
--- 

## 6. JavaScript Interactivity

JavaScript is used to enhance the user experience significantly, creating a dynamic interface:
- **Visual Charts & Graphs:**
    - `charts.js` renders dynamic progress bars on the main dashboard that turn **red** if spending exceeds category targets (50%/30%/20%).
    - **Chart.js** is utilised on the **Performance Dashboard** to render interactive bar charts showing annualised spending trends.
- **Interactive Budget Counter:** A dynamic monitoring system that calculates total expenditure against income in real-time. It provides immediate feedback by displaying:
    - A **Green** success message when income is perfectly allocated.
    - A **Red** warning alert when spending exceeds available income.
- **Inline Editing & Deletion:** `dashboard.js` enables users to:
    - Edit **expense** and **income** descriptions and amounts directly within the dashboard cards (AJAX).
    - Delete expenses and income entries seamlessly, triggering instant recalculations of the budget totals.

These features create a more engaging single-page application feel while remaining maintained by a Flask backend.

---

## 7. Hosting and Deployment

### 7.1 Version Control
The project is managed using Git and hosted on GitHub:
- Clear commit history
- Logical file structure
- Separation of concerns between backend and frontend assets

### 7.2 Render Deployment
The application is deployed using **Render.com** and is accessible here: [https://myfinancialtracker.onrender.com](https://myfinancialtracker.onrender.com).

To deploy this application yourself:
1.  **Create a Render Account:** Sign up at [render.com](https://render.com/).
2.  **New Web Service:** Click "New +" and select "Web Service".
3.  **Connect Repository:** Connect your GitHub account and select the `MyFinancialTracker` repository.
4.  **Configure Settings:**
    - **Runtime:** `Python 3`
    - **Build Command:** `pip install -r requirements.txt`
    - **Start Command:** `gunicorn app:app`
5.  **Deploy:** Click "Create Web Service". Render will build the environment and launch the app.
6.  **Access:** Once the deployment status is "Live", the application is available at the provided `.onrender.com` URL.

> **Note on Performance:** This application is hosted on Render's **Free Tier**. The server will automatically "spin down" after 15 minutes of inactivity. If the site takes 50+ seconds to load effectively, it is simply "waking up" from this cold start. Subsequent interactions will be instant.

The hosted version mirrors the local development version and is fully functional and publicly accessible.

---

## 8. Testing Strategy

Manual testing was conducted throughout development to ensure functional correctness and user experience:

- **Functional Testing:** Verified that all CRUD operations (Create, Read, Update, Delete) for Incomes and Expenses function correctly and update the totals in real-time.
- **Desktop Layout Check:** Confirmed that the dashboard's 3-column layout renders correctly on standard desktop resolutions, ensuring all data is visible at a glance.
- **Edge Cases:** Tested inputs with empty fields and invalid numbers to ensure the application handles errors gracefully without crashing.
- **Cross-Browser Handling:** Checked rendering on Chrome and Safari to ensure consistent styling.

---

## 9. Challenges and Design Decisions

### 9.1 Routing vs Static Interfaces
For the purpose of demonstrating Python functionality and Flask routing capabilities, the application was explicitly designed with separate routes and templates for adding income (`/add-income`) and expenses (`/add-expense`). This approach allows for clear demonstration of server-side rendering, form handling, and request processing in Python.

If I were designing this application again without the specific requirement to demonstrate Python functionality, I would likely opt for a single-page application (SPA) approach or use modal dialogs on the main dashboard. This would allow users to add transactions without leaving the main view, providing a smoother user experience, though it would rely more heavily on client-side JavaScript rather than Flask's routing mechanisms.

---

## 10. Distinction-Level Features Summary

This project meets distinction criteria by:
- Demonstrating strong understanding of Flask routing and request handling
- Using multiple Python classes to model application data
- Integrating HTML, CSS, and JavaScript effectively
- Maintaining clean code structure and best practices
- Delivering a fully hosted and accessible web application

---

## 11. Conclusion

The Intentional Spending Tracker successfully fulfils the requirements of the Python Flask assignment. By combining a clear financial concept with structured Python code and a modern dashboard interface, the project demonstrates both technical competence and thoughtful application design appropriate for a distinction-level submission.

---

## 12. References

- **Nischa (Financial Educator):** *How to Budget in 2024: The 50/30/20 Rule.* [YouTube Video](https://www.youtube.com/watch?v=4sT2B2SRypo)
- **Flask Documentation:** Used for routing and template rendering reference.
- **MDN Web Docs:** Referenced for modern CSS Grid and Flexbox techniques.

