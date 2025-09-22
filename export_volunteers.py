import os, csv, re
from datetime import datetime
from helper_functions import create_connection, execute_read_query

def check_volunteer_table():
    volunteers_after = execute_read_query(f"select * from volunteers")
    for row in volunteers_after:
        print(row)


def main():

    # Create destination folder
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_directory = os.path.join(base_dir, 'sensitive_volunteer_data', datetime.now().strftime('%Y-%m-%d %H.%M'))
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Create csv file headers
    connection = create_connection()
    cursor = connection.execute("select * from volunteers limit 1;")
    column_names = list(map(lambda x: x[0], cursor.description))

    # Figure out how many files are needed
    counties = execute_read_query(f"select distinct county from volunteers")
    for county_tuple in counties:
        county = county_tuple[0] if county_tuple[0] and len(county_tuple[0]) > 2 else '_No County'
        county = re.sub(r'[^a-zA-Z0-9\s]', '', county)  # remove special characters for filename

        # Sometimes the file name contains question marks or other weird characters and will error out
        # Errors will be lumped into the "No County" file
        with open(os.path.join(output_directory, county + '.csv'), 'w', encoding="utf-8") as f:

            # Prepare data
            results = execute_read_query(f"SELECT * FROM volunteers WHERE county = '{county}';")

            # Write data
            writer = csv.writer(f)
            writer.writerow(column_names)
            writer.writerows(results)


if __name__ == "__main__":
    main()