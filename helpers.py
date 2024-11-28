import sqlite3
from time import asctime

conn = sqlite3.connect('FinLit.db', check_same_thread = False)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    status TEXT,
    account TEXT,
    name TEXT,
    amount NUMERIC,
    comment TEXT,
    date TEXT
) """)

conn.commit()

#Helping dictionaries
month = {"01":"January",
         "02":"February",
         "03":"March",
         "04":"April",
         "05":"May",
         "06":"June",
         "07":"July",
         "08":"August",
         "09":"September",
         "10":"October",
         "11":"November",
         "12":"December"}

#They are used for the system to know the current month
shorten_months = {"Jan":"January",
             "Feb":"February",
             "Mar":"March",
             "Apr":"April",
             "May":"May",
             "Jun":"June",
             "Jul":"July",
             "Aug":"August",
             "Sep":"September",
             "Oct":"October",
             "Nov":"November",
             "Dec":"December"}

#Useful variables
date = asctime().split() #[Day,Month,Date,Time,Year]
current_month = shorten_months[date[1]]
current_year = date[-1]

#Creating the table if it doesn't exist for the chosen month and year
cur.execute(f"""CREATE TABLE IF NOT EXISTS {current_month}_{current_year}_records(
    id INTEGER UNIQUE,
    status TEXT,
    account TEXT,
    name TEXT,
    amount NUMERIC,
    comment TEXT,
    date TEXT
)""")


def add(status,account,name,amount,date,comment):
    #Printing the info coming in
    print(f"status: {status}\naccount: {account}\nname: {name}\namount: {amount}\ndate: {date}\ncomment: {comment}\n")
    calen_date = date.split("-")

    #Getting the month and year
    chosen_month, chosen_year = month[calen_date[1]], calen_date[0]

    #Adding the transaction to the history log
    print(f"""INSERT INTO history(status,account,name,amount,comment,date) VALUES
             ("{status}","{account}","{name}",{amount},"{comment}","{calen_date[-1]} {chosen_month}, {chosen_year}")\n""")
    cur.execute(f"""INSERT INTO history(status,account,name,amount,comment,date) VALUES
             ("{status}","{account}","{name}",{amount},"{comment}","{calen_date[-1]} {chosen_month}, {chosen_year}")""")
    
    #Creating the table if it doesn't exist for the chosen month and year
    cur.execute(f"""CREATE TABLE IF NOT EXISTS {chosen_month}_{chosen_year}_records(
        id INTEGER UNIQUE,
        status TEXT,
        account TEXT,
        name TEXT,
        amount NUMERIC,
        comment TEXT,
        date TEXT
    )""")

    #Getting the last id from the history so it can be used for the chosen table
    id = cur.execute(f"SELECT id FROM history ORDER BY id DESC LIMIT 1").fetchone()[0]
    print("The last the id is: ",id,"\n")

    #Adding the transaction to the chosen table
    print(f"""INSERT INTO {chosen_month}_{chosen_year}_records(id,status,account,name,amount,comment,date) VALUES
             ({id},"{status}","{account}","{name}",{amount},"{comment}","{calen_date[-1]} {chosen_month}, {chosen_year}")""")
    cur.execute(f"""INSERT INTO {chosen_month}_{chosen_year}_records(id,status,account,name,amount,comment,date) VALUES
             ({id},"{status}","{account}","{name}",{amount},"{comment}","{calen_date[-1]} {chosen_month}, {chosen_year}")""")

    conn.commit()
    
    return 0

def calen_date_format(date):
    #Thi will convert the month to their month numbers
    months={"January":"01",
            "February":"02",
            "March":"03",
            "April":"04",
            "May":"05",
            "June":"06",
            "July":"07",
            "August":"08",
            "September":"09",
            "October":"10",
            "November":"11",
            "December":"12"}

    splited_date = date.split(" ")
    calen_date = f"{splited_date[-1]}-{months[splited_date[1][:-1]]}-{splited_date[0]}"
    return calen_date


def request_one(sql_query):
    '''
    This function will return requests from the database and set the values to zero if they equals to none
    '''
    #print(sql_query)
    request = cur.execute(sql_query).fetchone()
    if request[0] == None:
        return 0
    
    else:
        return request[0]


def month_tracker(month, year, status):
    '''
    This function will give out the account and amount information for the previous atmost 6 months
    '''

    #This will be used for as the x axis
    months = ["January","February","March","April",
            "May","June","July","August","September","October","November","December"]
    
    #The current year
    year = int(current_year)

    #The current month index for navigating
    month_index = months.index(month)

    #All the available tables in the data
    db_tables = cur.execute(f"SELECT name FROM sqlite_master WHERE type = 'table' ").fetchall()
    db_tables = [list(table) for table in db_tables]
    #print(db_tables)

    #Setting the length to track
    if len(db_tables) >= 8:
        track = 6
    
    else:
        track = len(db_tables) - 2

    #print(f"Current year: {year}\nMonth Index: {month_index}")

    #This is for the account information
    acc_info = [[],[]]

    for i in range((month_index - track), (month_index+1), 1):
        #If the months goes to the previous year
        if i == -1:
            year -= 1
        #print(f"{months[i]} {year}")
        current = f"{months[i]}_{year}_records"

        #Checking if there are records existing in the previous months
        for j in range(len(db_tables)):
            if current in db_tables[j][0]:
                acc_info[0].append(f"{months[i]} {year}")
                sum_amount = request_one(f"""SELECT SUM(amount) FROM {months[i]}_{year}_records WHERE status = '{status}' """)
                #Incase if there was no amount for the month
                if sum_amount == None: #Check and Updat ethe previous one
                    sum_amount = 0
                #else:
                    #sum_amount = sum_amount[0]
                acc_info[1].append(sum_amount)        

    return acc_info
    

#print(month_tracker("October","2024","Income"))

def savings_tracker(): #Works like a charm mixed with a geni - Do the same for the income section
    '''
    This function will track the savings amount and increment the balance to th next month
    '''

    #The available data to work with
    data = month_tracker(current_month, current_year, "Income")
    #print(data)

    #These will keep account of the incrementing
    incre_savings = 0

    #A list to hold the trend
    track = []

    for dates in data[0]:
        record = dates.split(" ")
        record = record[0] + "_" + record[1] + "_" + "records"
        inc_savings = request_one(f"""SELECT SUM(amount) FROM {record} WHERE status = 'Income' AND account = 'Savings' """)
        exp_savings = request_one(f"""SELECT SUM(amount) FROM {record} WHERE status = 'Expense' AND account = 'Savings' """)
        bal_savings = inc_savings - exp_savings
        incre_savings += bal_savings
        #print(incre_savings)
        track.append(incre_savings)
    
    return track

#print(savings_tracker())




# Ideas to implement
## Make a carousel on the graph located in the analysis page