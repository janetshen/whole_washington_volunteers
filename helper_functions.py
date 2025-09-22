from dotenv import load_dotenv
from dateutil import parser as date_parser
import os, sqlite3
from datetime import datetime, timedelta
from sqlite3 import Error

load_dotenv()

today = datetime.today().strftime('%Y-%m-%d')
yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
last_week = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')

# Data validation functions
def validate_date_format(date_string):
    isValidDate = True
    try:
        date_parser.parse(date_string)
    except ValueError:
        isValidDate = False

    return isValidDate


# Calculated constants #
## Earliest modified date we want for a volunteer
minimum_date = os.getenv('MINIMUM_DATE', 'not found in .env')
if minimum_date == 'yesterday':
    minimum_date = yesterday
elif minimum_date == 'last_week':
    minimum_date = last_week
elif validate_date_format(minimum_date):
    print('Valid custom date entered:', minimum_date)
else:
    raise ValueError('Invalid date format.  Check .env file for MINIMUM_DATE value, should be yyyy-mm-dd')


# sqlite3 functions

## Set up database connection
def create_connection(filename = yesterday):
    connection = None
    try:
        connection = sqlite3.connect('volunteers.db')
        #print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


## Create tables in sqlite database
def create_tables():

    create_volunteers_table = ("CREATE TABLE IF NOT EXISTS volunteers (\n"
                          "    volunteer_id TEXT UNIQUE,\n"
                          "    first_name TEXT,\n"
                          "    last_name TEXT,\n"
                          "    email TEXT,\n"
                          "    phone_number TEXT,\n"
                          "    address TEXT,\n"
                          "    city TEXT,\n"
                          "    state TEXT,\n"
                          "    zip TEXT,\n"
                          "    county TEXT,\n"
                          "    tags TEXT,\n"
                          "    taggings_url TEXT\n"
                          ");")
    execute_query(create_volunteers_table)

    # ['uuid' 'first_name' 'last_name' 'email' 'Phone Number'
    # 'can2_user_address' 'can2_user_city' 'can2_user_state' 'zip_code'
    # 'County' 'can2_user_tags' 'can2_subscription_status' 'can2_sms_status']

    create_raw_import_table = ("CREATE TABLE IF NOT EXISTS raw_import (\n"
                               "    volunteer_id TEXT UNIQUE,\n"
                               "    first_name TEXT,\n"
                               "    last_name TEXT,\n"
                               "    email TEXT,\n"
                               "    phone_number TEXT,\n"
                               "    address TEXT,\n"
                               "    city TEXT,\n"
                               "    state TEXT,\n"
                               "    zip TEXT,\n"
                               "    county TEXT,\n"
                               "    tags TEXT,\n"
                               "    email_status TEXT,\n"
                               "    sms_status TEXT\n"
                               ");")
    execute_query(create_raw_import_table)


## Run query, nothing returned
def execute_query(query):
    connection = create_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        #print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")
        print(query)


## Run query, return results
def execute_read_query(query):
    connection = create_connection()
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")
        print(query)


if __name__ == "__main__":
    print('Hello')