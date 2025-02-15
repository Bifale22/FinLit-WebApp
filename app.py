from flask import Flask, render_template, request, redirect
import helpers as hl

app = Flask(__name__)

green = ['rgba(64, 181, 173, 0.8)', 'rgba(196, 180, 84, 0.8)', 'rgba(64, 130, 109, 0.8)','rgba(64, 224, 208, 0.8)','rgba(0, 128, 128, 0.8)',
        'rgba(64, 158, 96, 0.8)','rgba(138, 154, 91, 0.8)','rgba(201, 204, 63, 0.8)','rgba(128, 128, 0, 0.8)','rgba(8, 143, 143, 0.8)',
        'rgba(69, 75, 27, 0.8)','rgba(170, 255, 0, 0.8)','rgba(2, 48, 32, 0.8)','rgba(95, 133, 117, 0.8)','rgba(53, 94, 59, 0.8)']

red = [#'rgba(114, 47, 55, 0.8)', 'rgba(227, 66, 52, 0.8)', 'rgba(164, 42, 4, 0.8)','rgba(99, 3, 48, 0.8)','rgba(124, 48, 48, 0.8)',
        #'rgba(255, 36, 0, 0.8)','rgba(194, 30, 86, 0.8)','rgba(255, 68, 51, 0.8)','rgba(227, 11, 92, 0.8)','rgba(74, 4, 4, 0.8)',
        'rgba(128, 0, 0, 0.8)','rgba(139, 0, 0, 0.8)','rgba(210, 4, 45, 0.8)','rgba(136, 8, 8, 0.8)','rgba(112, 41, 99, 0.8)']


@app.route("/")
def index():
    #Info for the first and second card
    try:
        # The below problem does exist
        total_inc_amount = hl.cur.execute(f"""SELECT SUM(amount) FROM {hl.current_month}_{hl.current_year}_records WHERE status = 'Income' """).fetchone()[0]
        total_exp_amount = hl.cur.execute(f"""SELECT SUM(amount) FROM {hl.current_month}_{hl.current_year}_records WHERE status = 'Expense' """).fetchone()[0]
    
    except hl.sqlite3.OperationalError:
        total_inc_amount = 0
        total_exp_amount = 0
    
    #Check if the data presented are equals to None
    if total_inc_amount == None:
        total_inc_amount = 0

    if total_exp_amount == None:
        total_exp_amount = 0

    if total_inc_amount == 0 and total_exp_amount == 0:
        checker = 0
    
    else:
        checker = 1

    #The savings info
    income_savings = hl.request_one(f"""SELECT SUM(amount) FROM history WHERE status = 'Income' AND account = 'Savings' """)
    expense_savings = hl.request_one(f"""SELECT SUM(amount) FROM history WHERE status = 'Expense' AND account = 'Savings' """)
    total_savings = income_savings - expense_savings

    #Calculating percentages for the last card
    bal = total_inc_amount - total_exp_amount

    #To avoid the zero division error
    if total_inc_amount == 0:
        inc_per = 0 #Income remaining percentage
        exp_per = 0 #Expense percentage

    else:
        inc_per = round( (bal / total_inc_amount) * 100 )
        exp_per = round( (total_exp_amount / total_inc_amount) * 100 )
    
    #Below is for the last card 
    inc_trans_no = hl.cur.execute(f"""SELECT COUNT(id) FROM history WHERE status = 'Income' """).fetchone()[0]
    exp_trans_no = hl.cur.execute(f"""SELECT COUNT(id) FROM history WHERE status = 'Expense' """).fetchone()[0]
    savings_no = hl.request_one(f"""SELECT COUNT(id) FROM history WHERE account = 'Savings' """)

    #In case if there's no data at all for the income and expense
    if inc_trans_no == None:
        inc_trans_no = 0
    
    if exp_trans_no == None:
        exp_trans_no = 0

    #The below information will used for the table
    table_data = hl.cur.execute(f"""SELECT * FROM {hl.current_month}_{hl.current_year}_records ORDER BY date DESC""").fetchall()

    #The graph section
    income_info = hl.month_tracker(hl.current_month,hl.current_year,"Income")
    expense_info = hl.month_tracker(hl.current_month,hl.current_year,"Expense")
    print(expense_info)
    data = {
        'labels': [months for months in income_info[0]],
        'datasets': [
            {
                'label': 'Income',
                'backgroundColor': green[0],
                'borderColor': green[0],
                'data': [inc_data for inc_data in income_info[1]],
            },
            {
                'label': 'Expense',
                'backgroundColor': red[0],
                'borderColor': red[0],
                'data': [exp_data for exp_data in expense_info[1]],
            },
            {
                'label': 'Balance',
                'backgroundColor': "orange",
                'borderColor': "orange",
                'data': [(income_info[1][i] - expense_info[1][i]) for i in range(len(income_info[1]))],
            }
        ]
    }

    hl.conn.commit()

    return render_template("index.html", title_name = "FinLit | Home",total_income = total_inc_amount, total_expense = total_exp_amount, total_savings = total_savings,
                            inc_no = inc_trans_no, exp_no = exp_trans_no, savings_no = savings_no, inc_per = inc_per, exp_per = exp_per, checker = checker,
                            table_data = table_data, data = data )

@app.route("/overview")
def overview():
    #Setting up the bar group
    income_info = hl.month_tracker(hl.current_month, hl.current_year,"Income")
    expense_info = hl.month_tracker(hl.current_month, hl.current_year,"Expense")

    data = {
        'labels': [month for month in income_info[0] if month in expense_info[0]],
        'datasets': [
            {
                'label': 'Income',
                'backgroundColor': green[0],
                'borderColor': green[0],
                'data': [inc_data for inc_data in income_info[1]],
            },
            {
                'label': 'Expense',
                'backgroundColor': red[0],
                'borderColor': red[0],
                'data': [exp_data for exp_data in expense_info[1]],
            }
        ]
    }

    hl.conn.commit()

    return render_template("overview.html", title_name = "FinLit | Overview", overview_sidebar = "active", data = data)

@app.route("/accounts")
def account():
    #Below is the date that will be display on the cards under account analysis
    total_inc_amount = hl.cur.execute(f"""SELECT SUM(amount) FROM {hl.current_month}_{hl.current_year}_records WHERE status = 'Income' """).fetchone()[0]
    total_exp_amount = hl.cur.execute(f"""SELECT SUM(amount) FROM {hl.current_month}_{hl.current_year}_records WHERE status = 'Expense' """).fetchone()[0]
    income_savings = hl.request_one(f"""SELECT SUM(amount) FROM history WHERE status ='Income' AND account = 'Savings' """)
    expense_savings = hl.request_one(f"""SELECT SUM(amount) FROM history WHERE status = 'Expense' AND account = 'Savings' """)
    
    #Check if the data presented are equals to None
    if total_inc_amount == None:
        total_inc_amount = 0
        income_savings = 0

        #This is for the table incase if there's no data
        checker = 0
    else:
        checker = 1

    if total_exp_amount == None:
        total_exp_amount = 0
        expense_savings = 0
    
    print(f"Total income: {total_inc_amount}")
    print(f"Total expense: {total_exp_amount}")
    print(f"Total savings: {income_savings}")

    #Calculating the balance
    bal = total_inc_amount - total_exp_amount

    #Avoiding the zero division error
    if total_inc_amount == 0 :
        per_contribution = 0
        print(f"Percentage Contribution: {per_contribution}")

    else:
        per_contribution = round( (bal / total_inc_amount) * 100 )
        print(f"Percentage Contribution: {per_contribution}")  

    #Getting the transaction number (total)
    trans_no = hl.cur.execute(f"""SELECT COUNT(id) FROM history""").fetchone()[0]

    #Calculating the savings remaining
    savings_rem = income_savings - expense_savings

    #Balance without savings
    ws_bal = bal - savings_rem

    #Below data is for the table
    table_data = hl.cur.execute(f"""SELECT id,account,name,amount,comment,date FROM {hl.current_month}_{hl.current_year}_records WHERE status = 'Income' ORDER BY date DESC""").fetchall()
    
    #Changing all the rows into list that I can add the calendar date for editing
    table_data = [list(data) for data in table_data]

    #Adding the calendar date for editing
    for i in range(len(table_data)):
        date = hl.calen_date_format(table_data[i][5])
        table_data[i].append(date)

    #For the first graph
    data = {
        'labels': ["Income","Expense","Balance","Savings"],
        'datasets': [{
            'label': ['Amount Contribution'],
            'backgroundColor': [g for g in green],
            'borderColor': [g for g in green],
            'data': [total_inc_amount,total_exp_amount,bal, savings_rem],
        }]
    }

    #Preparing details for the second graph
    graph_data = hl.cur.execute(f"""SELECT account, SUM(amount) FROM {hl.current_month}_{hl.current_year}_records WHERE status = 'Income' GROUP BY account """).fetchall()

    #For the graph at the bottom
    data1 = {
        'labels': [label[0] for label in graph_data],
        'datasets': [{
            'label': ['Account compositions'],
            'backgroundColor': [g for g in green],
            'borderColor': [g for g in green],
            'data': [amount[1] for amount in graph_data],
        }]
    }

    hl.conn.commit()

    return render_template("account.html", title_name = "FinLit | Account", account_sidebar = "active",
                            total_amount = total_inc_amount, bal = bal, per_contribution = per_contribution, trans_no = trans_no, income_savings = income_savings, savings_rem = savings_rem, ws_bal = ws_bal,
                            table_data = table_data, checker = checker, data = data, data1 = data1)

@app.route("/expense")
def expense():
    #Below is the date that will be display on the cards under account analysis
    total_inc_amount = hl.cur.execute(f"""SELECT SUM(amount) FROM {hl.current_month}_{hl.current_year}_records WHERE status = 'Income' """).fetchone()[0]
    total_exp_amount = hl.cur.execute(f"""SELECT SUM(amount) FROM {hl.current_month}_{hl.current_year}_records WHERE status = 'Expense' """).fetchone()[0]
    income_savings = hl.request_one(f"""SELECT SUM(amount) FROM history WHERE status ='Income' AND account = 'Savings' """)
    expense_savings = hl.request_one(f"""SELECT SUM(amount) FROM history WHERE status = 'Expense' AND account = 'Savings' """)
    
    #Check if the data presented are equals to None
    if total_exp_amount == None:
        total_exp_amount = 0
        expense_savings = 0

        #This is for the table incase if there's no data
        checker = 0
    else:
        checker = 1

    if total_inc_amount == None:
        total_inc_amount = 0
        income_savings = 0

    #Calculating the balance
    bal = total_inc_amount - total_exp_amount

    #Avoiding the zero division error
    if total_inc_amount == 0 :
        per_contribution = 0
        print(f"Percentage Contribution: {per_contribution}")

    else:
        per_contribution = round( (total_exp_amount / total_inc_amount) * 100 )
        print(f"Percentage Contribution: {per_contribution}")

    #Getting the transaction number (total)
    trans_no = hl.cur.execute(f"""SELECT COUNT(id) FROM history""").fetchone()[0]

    #Calculating the savings remaining
    savings_rem = income_savings - expense_savings

    #Balance without savings
    ws_bal = bal - savings_rem

    #Below data is for the table
    table_data = hl.cur.execute(f"""SELECT id,account,name,amount,comment,date FROM {hl.current_month}_{hl.current_year}_records WHERE status = 'Expense' ORDER BY date DESC""").fetchall()
    
    #Changing all the rows into list that I can add the calendar date for editing
    table_data = [list(data) for data in table_data]

    #Adding the calendar date for editing
    for i in range(len(table_data)):
        date = hl.calen_date_format(table_data[i][5])
        table_data[i].append(date)

    #For the graph
    data = {
        'labels': ["Income","Expense","Balance","Savings"],
        'datasets': [{
            'label': ['Amount Contribution'],
            'backgroundColor': [g for g in green],
            'borderColor': [g for g in green],
            'data': [total_inc_amount,total_exp_amount,bal, savings_rem],
        }]
    }

    #Preparing details for the second graph
    graph_data = hl.cur.execute(f"""SELECT account, SUM(amount) FROM {hl.current_month}_{hl.current_year}_records WHERE status = 'Expense' GROUP BY account """).fetchall()

    #For the graph at the bottom
    data1 = {
        'labels': [label[0] for label in graph_data],
        'datasets': [{
            'label': ['Account compositions'],
            'backgroundColor': [g for g in green],
            'borderColor': [g for g in green],
            'data': [amount[1] for amount in graph_data],
        }]
    }

    hl.conn.commit()

    return render_template("expense.html", title_name = "FinLit | Expense", expense_sidebar = "active",
                            total_amount = total_exp_amount, bal = bal, per_contribution = per_contribution, trans_no = trans_no, expense_savings = expense_savings, savings_rem = savings_rem, ws_bal = ws_bal,
                            table_data = table_data, checker = checker, data = data, data1 = data1)

@app.route("/savings")
def savings():

    #Below are details of the account analysis card

    #Savings as an income
    income_savings = hl.cur.execute(f"""SELECT SUM(amount) FROM history WHERE status = 'Income' AND account = 'Savings' """).fetchone()[0]

    #Savings as an expense
    expense_savings = hl.cur.execute(f"""SELECT SUM(amount) FROM history WHERE status = 'Expense' AND account = 'Savings' """).fetchone()[0]

    #Checking for None values
    if (income_savings == None ) and (expense_savings == None):
        income_savings = 0
        expense_savings = 0

    elif (income_savings != None) and (expense_savings == None):
        expense_savings = 0

    elif (income_savings == None) and (expense_savings != None):
        income_savings = 0

    #Savings balance
    savings_bal = income_savings - expense_savings

    #Checking for any none value
    if savings_bal == None:
        savings_bal = 0
        #This is for the graph if there's a none value
        checker = 0

    else:
        #This is for the graph if there's a value
        checker = 1

    #Getting the total expense and income in order to calculate the balance
    total_income = hl.request_one(f"""SELECT SUM(amount) FROM {hl.current_month}_{hl.current_year}_records WHERE status = 'Income' """)    
    total_expense = hl.request_one(f"""SELECT SUM(amount) FROM {hl.current_month}_{hl.current_year}_records WHERE status = 'Expense' """)


    #Calcuting the balance
    bal = total_income - total_expense

    #Getting the savings percentage
    if total_income == 0:
        #This avoids the zero division
        savings_per = 0
    else:
        savings_per = round( savings_bal / total_income * 100)

    #Getting the number of acounts
    savings_trans = hl.cur.execute(f"""SELECT COUNT(amount) FROM history WHERE status = 'Income' AND account = 'Savings' """).fetchone()[0]

    #Checking for any None values
    if savings_trans == None:
        savings_trans = 0

    #Balance without savings
    ws_bal = bal - savings_bal #Needs fixing IF One account is placed

    if bal == 0:
        ws_bal = 0

    #Preparing details for the first graph (Use these for account analysis)
    graph_data = hl.cur.execute(f"""SELECT account, SUM(amount) FROM {hl.current_month}_{hl.current_year}_records WHERE status = 'Income' GROUP BY account """).fetchall()

    #For the first graph (SAVINGS)
    data = {
        'labels': ["Savings Total","Savings Used","Savings Balance"],
        'datasets': [{
            'label': ['Amount Contribution'],
            'backgroundColor': [g for g in green],
            'borderColor': [g for g in green],
            'data': [income_savings, expense_savings, savings_bal],
        }]
    }

    #Below information is for the table
    table_data = hl.cur.execute(f"""SELECT * FROM history WHERE account = 'Savings' ORDER BY date DESC""").fetchall()

    #Changing all the rows into list that I can add the calendar date for editing
    table_data = [list(data) for data in table_data]

    #Adding the calendar date for editing
    for i in range(len(table_data)):
        date = hl.calen_date_format(table_data[i][-1])
        table_data[i].append(date)

    #For the line graph
    months = hl.month_tracker(hl.current_month,hl.current_year,"Income")
    amounts = hl.savings_tracker() 
    data1 = {
        'labels': months[0],
        'datasets': [{
            'label': ['Savings'],
            'backgroundColor': [g for g in green],
            'borderColor': [g for g in green],
            'data': amounts,
        }]
    }
    

    return render_template("savings.html", title_name = "FinLit | Savings", savings_sidebar = "active",
                            savings_bal = savings_bal, bal = bal, savings_per = savings_per, savings_trans = savings_trans, income_savings = income_savings, expense_savings = expense_savings, ws_bal = ws_bal,
                            data = data, table_data = table_data, data1 = data1)

@app.route("/add_account", methods=["POST","GET"])
def add_account():
    if request.method == "POST":
        #If back-end checking for essential input field
        if (request.form["account"] == '') or (request.form["name"] == '') or (request.form["amount"] == '') or (request.form["date"] == ''):
            return render_template("error.html")
        hl.add(request.form["status"],request.form["account"],request.form["name"],request.form["amount"],request.form["date"],request.form["comment"])
        print(request.form)
        return redirect("/accounts")

    else:

        #Below data is for the table
        table_data = hl.cur.execute(f"""SELECT account,name,amount,comment,date FROM {hl.current_month}_{hl.current_year}_records WHERE status = 'Income' ORDER BY date DESC""").fetchall()

        #This is for the data which gives all the accounts ever existed
        account_names = hl.cur.execute(f"""SELECT DISTINCT(account) FROM history WHERE status = 'Income' """).fetchall()

        return render_template("add_form.html", title_name = "FinLit | Add Account", table_data = table_data, account_names = account_names )

@app.route("/add_expense", methods=["POST","GET"])
def add_expense():
    if request.method == "POST":

        #If back-end checking for essential input field
        if (request.form["account"] == '') or (request.form["name"] == '') or (request.form["amount"] == '') or (request.form["date"] == ''):
            return render_template("error.html")

        hl.add(request.form["status"],request.form["account"],request.form["name"],request.form["amount"],request.form["date"],request.form["comment"])
        print(request.form)
        return redirect("/expense")

    else:

        #Below data is for the table
        table_data = hl.cur.execute(f"""SELECT account,name,amount,comment,date FROM {hl.current_month}_{hl.current_year}_records WHERE status = 'Expense' ORDER BY date DESC""").fetchall()

        #This is for the data which gives all the accounts ever existed
        account_names = hl.cur.execute(f"""SELECT DISTINCT(account) FROM history WHERE status = 'Expense' """).fetchall()

        return render_template("add_expense.html", title_name = "FinLit | Add Expense", table_data = table_data, account_names = account_names )

@app.route("/add_savings", methods=["POST","GET"])
def add_savings():
    if request.method == "POST":

        #If back-end checking for essential input field
        if (request.form["account"] == '') or (request.form["name"] == '') or (request.form["amount"] == '') or (request.form["date"] == ''):
            return render_template("error.html")

        hl.add(request.form["status"],request.form["account"],request.form["name"],request.form["amount"],request.form["date"],request.form["comment"])
        print(request.form)
        return redirect("/savings")

    else:

        #Below data is for the table
        table_data = hl.cur.execute(f"""SELECT * FROM history WHERE status = 'Income' AND account = 'Savings' ORDER BY date DESC""").fetchall()

        #This is for the data which gives all the accounts ever existed
        account_names = hl.cur.execute(f"""SELECT DISTINCT(account) FROM history WHERE status = 'Income' """).fetchall()

        return render_template("add_savings.html", title_name = "FinLit | Add Savings", table_data = table_data, account_names = account_names)

@app.route("/edit", methods=["POST"])
def edit():
    #Getting information needed to edit the transaction from the history and the given table
    needed_info = request.form["edit_trans"].split(",") #[id, date and month, table_name(for redirecting)]
    chosen_id = int(needed_info[0])
    chosen_month = needed_info[1][3:]
    chosen_year = needed_info[2][1:]

    #Handling the date
    calen_date = request.form["date"].split("-")

        #Getting the month and year
    chosen_month, chosen_year = hl.month[calen_date[1]], calen_date[0]

    #If it is a savings
    if needed_info[-1] == "savings":
        print("Yep")
        print(f"\nBasic info of the chosen account:\nChosen ID: {chosen_id}\nChosen Month: {chosen_month}\nChosen Year: {chosen_year}\nRedirecting route: /{needed_info[-1]}\n")
        print(f"Info that came in:\nStatus: {request.form["status"]}\nName: {request.form["name"]}\nAmount: {request.form["amount"]}\nComment: {request.form["comment"]}\nDate: {calen_date[-1]} {chosen_month}, {chosen_year}\n")
        
        #Going to edit the history table
        print(f"""UPDATE history SET
                        name = "{request.form["name"]}", amount = {request.form["amount"]}, comment = "{request.form["comment"]}", date = "{calen_date[-1]} {chosen_month}, {chosen_year}"
                        WHERE id = {chosen_id} \n""")
        hl.cur.execute(f"""UPDATE history SET
                        name = "{request.form["name"]}", amount = {request.form["amount"]}, comment = "{request.form["comment"]}", date = "{calen_date[-1]} {chosen_month}, {chosen_year}"
                        WHERE id = {chosen_id} \n""")
        
        #Going to edit the chosen table
        print(f"""UPDATE {chosen_month}_{chosen_year}_records SET 
                        name = "{request.form["name"]}", amount = {request.form["amount"]}, comment = "{request.form["comment"]}", date = "{calen_date[-1]} {chosen_month}, {chosen_year}"
                        WHERE id = {chosen_id} \n""")
        hl.cur.execute(f"""UPDATE {chosen_month}_{chosen_year}_records SET 
                        name = "{request.form["name"]}", amount = {request.form["amount"]}, comment = "{request.form["comment"]}", date = "{calen_date[-1]} {chosen_month}, {chosen_year}"
                        WHERE id = {chosen_id} """)

    else:
        print(f"\nBasic info of the chosen account:\nChosen ID: {chosen_id}\nChosen Month: {chosen_month}\nChosen Year: {chosen_year}\nRedirecting route: /{needed_info[-1]}\n")
        print(f"Info that came in:\nAccount: {request.form["account"]}\nName: {request.form["name"]}\nAmount: {request.form["amount"]}\nComment: {request.form["comment"]}\nDate: {calen_date[-1]} {chosen_month}, {chosen_year}\n")

        #Going to edit the history table
        print(f"""UPDATE history SET
                        account = "{request.form["account"]}", name = "{request.form["name"]}", amount = {request.form["amount"]}, comment = "{request.form["comment"]}", date = "{calen_date[-1]} {chosen_month}, {chosen_year}"
                        WHERE id = {chosen_id} \n""")
        hl.cur.execute(f"""UPDATE history SET
                        account = "{request.form["account"]}", name = "{request.form["name"]}", amount = {request.form["amount"]}, comment = "{request.form["comment"]}", date = "{calen_date[-1]} {chosen_month}, {chosen_year}"
                        WHERE id = {chosen_id} \n""")

        #Going to edit the chosen table
        print(f"""UPDATE {chosen_month}_{chosen_year}_records SET 
                        account = "{request.form["account"]}", name = "{request.form["name"]}", amount = {request.form["amount"]}, comment = "{request.form["comment"]}", date = "{calen_date[-1]} {chosen_month}, {chosen_year}"
                        WHERE id = {chosen_id} \n""")
        hl.cur.execute(f"""UPDATE {chosen_month}_{chosen_year}_records SET 
                        account = "{request.form["account"]}", name = "{request.form["name"]}", amount = {request.form["amount"]}, comment = "{request.form["comment"]}", date = "{calen_date[-1]} {chosen_month}, {chosen_year}"
                        WHERE id = {chosen_id} """)

    #print(request.form)

    hl.conn.commit()

    return redirect(f"/{needed_info[-1]}")


@app.route("/delete", methods=["POST"])
def delete():
    #Getting information needed to delete the transaction from the history and the given table
    needed_info = request.form["delete_trans"].split(",") #[id, date and month, table_name(for redirecting)]
    chosen_id = int(needed_info[0])
    chosen_month = needed_info[1][3:]
    chosen_year = needed_info[2][1:]

    #Deleting it from the history table
    hl.cur.execute(f"DELETE FROM history WHERE id = {chosen_id}")
    print(f"DELETE FROM history WHERE id = {chosen_id}\n")

    #Deleting it from the individual table
    hl.cur.execute(f"DELETE FROM {chosen_month}_{chosen_year}_records WHERE id = {chosen_id}")
    print(f"DELETE FROM {chosen_month}_{chosen_year}_records WHERE id = {chosen_id}")
    hl.conn.commit()

    print(f"\nBasic info of account:\nChosen ID: {chosen_id}\nChosen Month: {chosen_month}\nChosen Year: {chosen_year}\nRedirecting route: /{needed_info[-1]}\n")
    return redirect(f"/{needed_info[-1]}")

