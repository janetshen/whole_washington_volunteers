from helper_functions import (
    create_connection, create_tables, execute_query, execute_read_query)
import pandas as pd


def main():

    connection = create_connection()
    create_tables()

    # Open .csv file, read data
    # Downloaded from https://admin.actionnetwork.org/reports/initial-download-for-python-code-janet-shen/manage
    df = pd.read_csv("data.csv")

    # Rename columns
    # ['uuid' 'first_name' 'last_name' 'email' 'Phone Number'
    # 'can2_user_city' 'can2_user_state' 'zip_code'
    # 'County' 'can2_user_tags' 'can2_subscription_status' 'can2_sms_status']
    df.rename(columns={
        'uuid' : 'volunteer_id',
        'Phone Number' : 'phone_number',
        'can2_user_city' : 'city',
        'can2_user_state' : 'state',
        'zip_code' : 'zip',
        'County' : 'county',
        'can2_user_tags' : 'tags',
        'can2_subscription_status' : 'email_status',
        'can2_sms_status' : 'sms_status'}, inplace=True)

    df.to_sql("raw_import", connection, if_exists="replace", index=False)

    cleanup_query = (f"select\n"
                     f"    volunteer_id,\n"
                     f"    first_name,\n"
                     f"    last_name,\n"
                     f"    case when email_status = 'subscribed' then email else NULL end as email,\n"
                     f"    case when sms_status = 'subscribed' then phone_number else NULL end as phone_number,\n"
                     f"    city,\n"
                     f"    state,\n"
                     f"    zip,\n"
                     f"    county,\n"
                     f"    tags,\n"
                     f"    'https://actionnetwork.org/api/v2/people/' || volunteer_id || '/taggings' AS taggings_url\n"
                     f"    from raw_import\n"
                     f"    where email_status = 'subscribed' or sms_status = 'subscribed';")
    cleaned_results_1 = execute_read_query(cleanup_query)

    for volunteer_id, first_name, last_name, email, phone_number, city, state, zip, county, tags, taggings_url in cleaned_results_1:
        email = email.replace("'", "''") if email and "'" in email else email
        phone_number = phone_number.replace("'", "''") if phone_number and "'" in phone_number else phone_number
        first_name = first_name.replace("'", "''") if first_name and "'" in first_name else first_name
        last_name = last_name.replace("'", "''") if last_name and "'" in last_name else last_name
        city = city.replace("'", "''") if city and "'" in city else city
        state = state.replace("'", "''") if state and "'" in state else state
        zip = zip.replace("'", "''") if zip and "'" in zip else zip
        county = county.replace("'", "''") if county and "'" in county else county

        create_volunteers = (
            f"INSERT OR REPLACE INTO \n"
            f"    volunteers (volunteer_id, first_name, last_name, email, phone_number, city, state, zip, county, tags, taggings_url) \n"
            f"VALUES \n"
            f"    ('{volunteer_id}', '{first_name}', '{last_name}', '{email}', '{phone_number}', '{city}', '{state}', '{zip}', '{county}', '{tags}', '{taggings_url}');"
        )
        execute_query(create_volunteers)

    cleaned_results_2 = execute_read_query("select * from volunteers")
    for row in cleaned_results_2:
        print(row)

    execute_query(f"drop table raw_import;")


if __name__ == "__main__":
    main()