import os
from dotenv import load_dotenv
import requests, re, zipcodes

from helper_functions import (
    minimum_date,
    execute_query, execute_read_query)

# Load .env file
load_dotenv()
api_token = os.getenv("API_TOKEN")
update_tags_and_counties_for_recently_changed_volunteers_only = os.getenv("UPDATE_RECENT_ONLY")  #defaults to true

# Start REST API session
session = requests.Session()

# Authentication details
url_root = 'https://actionnetwork.org/api/v2/'
headers = {"Content-Type": "application/json",
           "OSDI-API-Token": api_token}


# Set up database connection
def tag_generator():
    # REST API endpoint we're communicating with
    url = url_root + "tags"

    first_page = session.get(url, headers=headers).json()
    yield first_page
    num_pages = first_page['total_pages']

    for tag_page in range(2, num_pages + 1):
        next_page = session.get(url, headers=headers, params={'page': tag_page}).json()
        yield next_page


def taggings_generator(url):
    # REST API endpoint we're communicating with

    first_page = session.get(url, headers=headers).json()
    yield first_page
    num_pages = first_page['total_pages']

    for tag_page in range(2, num_pages + 1):
        next_page = session.get(url, headers=headers, params={'page': tag_page}).json()
        yield next_page


def get_volunteers():

    volunteers_to_update = []  # (volunteer_id, zip_code, taggings_url)

    def volunteer_generator():

        # REST API endpoint we're communicating with
        url = url_root + "people?filter=modified_date%20gt%20'" + minimum_date + "'"
        #url = url_root + "people"

        # First response we get will be one of many pages (search web for 'REST API pagination' for details)
        first_page = session.get(url, headers=headers).json()

        # Yield makes it so the computer doesn't run out of memory (search web for 'python yield' for details)
        yield first_page

        # ActionNetwork's people resource is unusual in that it doesn't tell you up front how many pages to expect
        # The best we can do is check if the current page has a reference to a "next" page, as we go
        has_next_page = 'next' in "\n".join(first_page.get('_links'))  # true/false value
        current_page = 1

        while has_next_page and current_page:
            current_page += 1
            next_page = session.get(url, headers=headers, params={'page': current_page}).json()
            yield next_page
            has_next_page = 'next' in "\n".join(next_page.get('_links'))  # true/false value

    # Loop through each page, pulling out important information
    for page in volunteer_generator():
        volunteers = page.get('_embedded').get('osdi:people')

        for v in volunteers:
            email = v.get('email_addresses')[0].get('address') if v.get('email_addresses')[0] and v.get('email_addresses')[0].get('status') == 'subscribed' else None
            phone_number = v.get('phone_numbers')[0].get('number') if v.get('phone_numbers')[0] and v.get('phone_numbers')[0].get('status') == 'subscribed' else None
            volunteer_id = v.get('identifiers')[0].replace('action_network:', '')

            if email or phone_number:

                email = email.replace("'", "''") if email and "'" in email else email
                phone_number = phone_number.replace("'", "''") if phone_number and "'" in phone_number else phone_number

                first_name = v.get('given_name')
                first_name = first_name.replace("'", "''") if first_name and "'" in first_name else first_name

                last_name = v.get('family_name')
                last_name = last_name.replace("'", "''") if last_name and "'" in last_name else last_name

                city = v.get('postal_addresses')[0].get('locality')
                city = city.replace("'", "''") if city and "'" in city else city

                state = v.get('postal_addresses')[0].get('region')
                state = state.replace("'", "''") if state and "'" in state else state

                zip_code = v.get('postal_addresses')[0].get('postal_code')
                zip_code = zip_code.replace("'", "''") if zip_code and "'" in zip_code else zip_code

                taggings_url = v.get('_links').get('osdi:taggings').get('href')

                create_volunteers = (
                    f"INSERT OR REPLACE INTO \n"
                    f"    volunteers (volunteer_id, first_name, last_name, email, phone_number, city, state, zip, taggings_url) \n"
                    f"VALUES \n"
                    f"    ('{volunteer_id}', '{first_name}', '{last_name}', '{email}', '{phone_number}', '{city}', '{state}', '{zip_code}', '{taggings_url}');"
                )
                execute_query(create_volunteers)

                volunteers_to_update.append((volunteer_id, zip_code, taggings_url))  # needs to be a tuple

            else:
                execute_query(f"delete from volunteers where volunteer_id='{volunteer_id}'")

    return volunteers_to_update


def get_tag_dictionary():

    tag_dictionary = {}

    for tag_page in tag_generator():
        for tag in tag_page.get('_embedded').get('osdi:tags'):
            tag_id = tag.get('identifiers')[0].replace('action_network:', '')
            if tag_id not in tag_dictionary.keys():
                tag_dictionary.update({tag_id: tag.get('name')})

    return tag_dictionary


def get_taggings(tag_dictionary, volunteers_to_update=[]):

    # If no volunteers specified, update tags of entire table
    if len(volunteers_to_update) > 0:
        volunteers = [(i[0], i[2]) for i in volunteers_to_update]
    else:
        volunteers = execute_read_query("select volunteer_id, taggings_url from volunteers")

    # Update tags
    for v_id, taggings_url in volunteers:
        tag_names = []
        for page in taggings_generator(taggings_url):
            taggings = page.get('_links').get('osdi:taggings')
            if len(taggings) > 0:
                for tagging in taggings:
                    tag_id = tagging.get('href')
                    tag_id = re.search('[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', tag_id).group(0)
                    tag_name = tag_dictionary.get(tag_id, 'not found')
                    if tag_name not in tag_names:
                        tag_names.append(tag_name)
        tag_names_string = ", ".join(tag_names) if len(tag_names) > 0 else None

        update_volunteer_tags = (f"UPDATE volunteers SET tags = '{tag_names_string}' WHERE volunteer_id = '{v_id}'")
        execute_query(update_volunteer_tags)


def get_counties(volunteers_to_update=[]):

    # If no volunteers specified, update counties of entire table
    if len(volunteers_to_update) > 0:
        volunteers = [(i[ 0], i[1]) for i in volunteers_to_update]
    else:
        volunteers = execute_read_query("select volunteer_id, zip from volunteers")

    # Update database with county names
    for v_id, zip_code in volunteers:

        # Use clean zip codes to look up county
        if zip_code and re.match('^[0-9]{5}(?:-[0-9]{4})?$', zip_code) and len(zipcodes.matching(zip_code)) > 0:
            county = zipcodes.matching(zip_code)[0].get('county')  # look up using first five characters of zip
            county = county.replace("'", "") if county and "'" in county else county
            execute_query(f"UPDATE volunteers SET county = '{county}' WHERE volunteer_id = '{v_id}'")
            #print('correct', zip_code, county, zipcodes.matching(zip_code))
        elif zip_code and re.match('^[0-9]{5}(?:-[0-9]{4})?$', zip_code) and len(zipcodes.matching(zip_code)) == 0:
            print('Zip code not recognized by zipcodes library: {' + zip_code + '}')
        elif zip_code and zip_code != 'None':
            print('Data cleaning needed for zipcode {' + zip_code + '} and volunteer_id {' + v_id + '}')
        else:
            print('No zip code found for volunteer_id:' + v_id)


def main():

    volunteers_to_update = get_volunteers()  # overwrites recently modified volunteers
    tag_dictionary = get_tag_dictionary()  # for get_taggings

    if update_tags_and_counties_for_recently_changed_volunteers_only:
        # For updating recently modified volunteers
        get_taggings(tag_dictionary, volunteers_to_update)  # populates taggings in volunteers table
        get_counties(volunteers_to_update)  # populates counties in volunteers table

    else:
        # For just after importing from csv
        get_taggings(tag_dictionary)  # populates taggings in volunteers table
    get_counties()  # populates counties in volunteers table


if __name__ == "__main__":
    main()