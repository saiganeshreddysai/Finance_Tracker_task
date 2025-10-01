# Personal Finance Tracker
This is a web-based Personal Finance Tracker application built with **Python (Flask)**. It allows users to log expenses, set monthly budgets for different categories, and view reports to track spending and monitor budget limits.

##  Core Features
* Record transactions with date, amount, category, and description.
* Set monthly spending limits for specific categories.
* Receive a warning if a new expense exceeds the budget for that category.
* View total monthly spending and a detailed category-by-category comparison against the set budget.
*  Data is saved locally in `finance_tracker_data.json`.

**##Requirements**
   python version 3 and Flask

## Installation 
   pip install Flask
   
##cloning git
   git clone https://github.com/saiganeshreddysai/Finance_Tracker_task
   
##  Steps to Run the Application
1. Navigate to the project directory (`cd <path to your finance_tracker>`).
2. Execute the main Python file to start the Flask development server:
   in bash/terminal (type below command):
   python app.py
    
3. Open your web browser and navigate to the address shown in your terminal:
   the address shown in my terminal is given below:
   (http://127.0.0.1:5000/)

4. Use the below option 
   ###Set Budget -
   for setting monthly budgets for each different category
   ###Log Expense-
   using this option you can log your daily expenses along with date, category, amount and also description like for food category desc: is lunch, dinner,etc
   ###Reports- 
   using this option you can view your monthly reports for each different month for each different category where you can see your spendings total , budget and        remaining balance amoutn that can be spent in that particular category for that month 
