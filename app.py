# app.py
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash

# --- Configuration and Data Storage ---
DATA_FILE = 'finance_tracker_data.json'
CATEGORIES = ["Food", "Transport", "Entertainment", "Utilities", "Shopping", "Health", "Other"]

def load_data():
    """Loads expense and budget data from the JSON file."""
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Start with fresh data if file is missing or corrupted
        data = {'expenses': [], 'budgets': {}}
    return data

def save_data(data):
    """Saves expense and budget data to the JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Load data immediately when the app starts
DATA = load_data()

# --- Core Logic Functions (NOW CORRECTED) ---

def calculate_monthly_spending(month_year):
    """Calculates total and category spending for a given YYYY-MM by reading DATA."""
    monthly_total = 0.0
    category_totals = {}
    
    for expense in DATA['expenses']:
        # Ensure date is available and in YYYY-MM-DD format before slicing
        if 'date' in expense and len(expense['date']) >= 7:
            expense_month = expense['date'][:7] 
        else:
            continue

        if expense_month == month_year:
            amount = expense.get('amount', 0.0)
            category = expense.get('category', 'Uncategorized')
            
            monthly_total += amount
            category_totals[category] = category_totals.get(category, 0.0) + amount
            
    return monthly_total, category_totals


def check_budget_alert(date_str, category):
    """Checks budget for the specific month and category and returns an alert message."""
    month_year = date_str[:7]
    budget = DATA['budgets'].get(category, {}).get(month_year, 0.0)
    
    if budget <= 0:
        return None 

    _, category_spending = calculate_monthly_spending(month_year)
    current_spent = category_spending.get(category, 0.0)
    
    if current_spent > budget:
        over_by = current_spent - budget
        return (f"!!! BUDGET ALERT !!! You are OVER BUDGET by Rs{over_by:.2f} "
                f"for {category} in {month_year}. Budget: Rs{budget:.2f}, Spent: Rs{current_spent:.2f}")
    return None

# --- Flask App Setup and Routes ---
app = Flask(__name__)
app.secret_key = 'supersecretkeyforflash' 

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

@app.route('/log', methods=['GET', 'POST'])
def log_expense_web():
    """Route for logging a new expense."""
    if request.method == 'POST':
        try:
            date_str = request.form['date']
            amount = float(request.form['amount'])
            category = request.form['category']
            description = request.form.get('description', 'N/A') or 'N/A'

            if amount <= 0:
                flash("Amount must be positive.", 'danger')
                return redirect(url_for('log_expense_web'))

            new_expense = {
                'date': date_str,
                'amount': amount,
                'category': category,
                'description': description
            }
            DATA['expenses'].append(new_expense)
            save_data(DATA) 
            
            alert_message = check_budget_alert(date_str, category)
            if alert_message:
                flash(alert_message, 'warning')
            
            flash("Expense logged successfully!", 'success')
            return redirect(url_for('index'))
            
        except ValueError:
            flash("Invalid input. Please check the amount and date formats.", 'danger')
            return redirect(url_for('log_expense_web'))
        except Exception as e:
            flash(f"An unexpected error occurred: {e}", 'danger')
            return redirect(url_for('log_expense_web'))

    today_date = datetime.now().strftime("%Y-%m-%d")
    return render_template('log_expense.html', categories=CATEGORIES, today_date=today_date)


@app.route('/budget', methods=['GET', 'POST'])
def set_budget_web():
    """Route for setting a monthly budget."""
    if request.method == 'POST':
        try:
            category = request.form['category'].strip().capitalize()
            month_year_str = request.form['month_year']
            amount = float(request.form['amount'])

            if not category or not month_year_str:
                flash("Category and month/year cannot be empty.", 'danger')
                return redirect(url_for('set_budget_web'))
            
            if amount < 0:
                flash("Budget amount cannot be negative.", 'danger')
                return redirect(url_for('set_budget_web'))

            if category not in DATA['budgets']:
                DATA['budgets'][category] = {}
                
            DATA['budgets'][category][month_year_str] = amount
            save_data(DATA)
            
            alert_message = check_budget_alert(month_year_str + "-01", category) 
            if alert_message:
                flash(alert_message, 'warning')

            flash(f"Budget of Rs{amount:.2f} set for {category} in {month_year_str}.", 'success')
            return redirect(url_for('index'))

        except ValueError:
            flash("Invalid amount or date format. Please use YYYY-MM.", 'danger')
            return redirect(url_for('set_budget_web'))

    current_month_year = datetime.now().strftime("%Y-%m")
    return render_template('set_budget.html', categories=CATEGORIES, current_month_year=current_month_year)


@app.route('/reports', methods=['GET', 'POST'])
def show_basic_reports_web():
    """Route for viewing spending reports (NOW CORRECTED)."""
    
    report_data = None
    month_year = datetime.now().strftime("%Y-%m") # Default to current month

    if request.method == 'POST':
        month_year = request.form.get('month_year', month_year)
        
        # 1. Calculate spending for the selected month
        total_spending, category_spending = calculate_monthly_spending(month_year)
        
        # 2. Prepare data for comparison
        all_categories = set(category_spending.keys()).union(DATA['budgets'].keys())
        sorted_categories = sorted(list(all_categories))
        
        category_reports = []
        for category in sorted_categories:
            spent = category_spending.get(category, 0.0)
            budget = DATA['budgets'].get(category, {}).get(month_year, 0.0)
            
            balance = budget - spent
            status_text = ""
            is_over_budget = False
            
            if budget > 0:
                if balance < 0:
                    status_text = f"OVER BUDGET by Rs{abs(balance):.2f}"
                    is_over_budget = True
                elif balance == 0:
                    status_text = "Budget met."
                else:
                    status_text = f"Remaining: Rs{balance:.2f}"
            elif spent > 0:
                status_text = "No budget set."

            if spent > 0 or budget > 0: # Only show relevant categories
                category_reports.append({
                    'category': category,
                    'spent': f"{spent:.2f}",
                    'budget': f"{budget:.2f}",
                    'status': status_text,
                    'is_alert': is_over_budget
                })

        # Final structure passed to the HTML template
        report_data = {
            'month': month_year,
            'total_spending': f"{total_spending:.2f}",
            'category_reports': category_reports
        }

    return render_template('reports.html', 
                           report_data=report_data, 
                           current_month_year=month_year)


if __name__ == '__main__':
    app.run(debug=True)