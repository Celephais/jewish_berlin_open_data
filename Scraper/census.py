"""
Quick and dirty scraper script to get the data from the minority census.
The website doesn't seem to handle large data queries well, so the script makes queries for every birthyear
and iterates over the pages. Writes the data direct to the sqlite database
"""

from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import sqlite3


def insert_into_db(census):
    try:
        c = conn.cursor()
        c.execute('INSERT INTO census (vorname, nachname, geboren, geburtsdatum, geburtsort, adresse, zusatz,'
                  ' bezirk) VALUES ("{}","{}","{}","{}","{}","{}","{}","{}")'.format(
            census['Vorname'],
            census['Nachname'],
            census['geboren'],
            census['Geburtsdatum'],
            census['Geburtsort'],
            census['Adresse'],
            census['Zusatz'],
            census['Bezirk']))
        conn.commit()
    except sqlite3.OperationalError:
        write_list_to_file(census, 'missing_census_data')


def write_list_to_file(missing_data_list, filename):
    """Write the list to csv file."""

    with open(filename, "a") as outfile:
        outfile.write(str(missing_data_list))
        outfile.write("\n")


# Data format is inconsistent but this configuration seems to have the best impact
def find_all_entries(all_entries):
    for i in range(0, len(all_entries), 2):
        list_entries = []
        temp_dict = {'geboren': None, 'Zusatz': None}
        entry_str = "Entry: {} \n".format(all_entries[i].get_text(separator=" | "))

        for entry in entry_str.split('|'):
            e = entry.strip()
            if e != '' and e != 'Entry:':
                list_entries.append(e)
        print(list_entries)

        temp_dict['Vorname'] = list_entries[0]
        temp_dict['Nachname'] = list_entries[1]
        if len(list_entries) == 7:
            temp_dict['Geburtsdatum'] = list_entries[2]
            temp_dict['Geburtsort'] = list_entries[3]
            temp_dict['Adresse'] = list_entries[4]
            temp_dict['Bezirk'] = list_entries[5]
        elif len(list_entries) == 8:
            if re.match(regex_date, list_entries[2]):
                temp_dict['Geburtsdatum'] = list_entries[2]
                temp_dict['Geburtsort'] = list_entries[3]
                temp_dict['Adresse'] = list_entries[4]
                temp_dict['Zusatz'] = list_entries[5]
                temp_dict['Bezirk'] = list_entries[6]
            else:
                temp_dict['geboren'] = list_entries[2]
                temp_dict['Geburtsdatum'] = list_entries[3]
                temp_dict['Geburtsort'] = list_entries[4]
                temp_dict['Adresse'] = list_entries[5]
                temp_dict['Bezirk'] = list_entries[6]
        elif len(list_entries) == 9:
            temp_dict['geboren'] = list_entries[2]
            temp_dict['Geburtsdatum'] = list_entries[3]
            temp_dict['Geburtsort'] = list_entries[4]
            temp_dict['Adresse'] = list_entries[5]
            temp_dict['Zusatz'] = list_entries[6]
            temp_dict['Bezirk'] = list_entries[7]

        # print(temp_dict)
        if len(list_entries) > 6:
            insert_into_db(temp_dict)
        else:
            write_list_to_file(list_entries, 'missing_census_data')


# range are the birthyears
for i in range(1820, 1940):
    print(i)
    conn = sqlite3.connect("adresses_31.db")
    regex_date = r"\d+\.\d+\.\d+"
    regex_counter = r"\d+"
    page = urlopen(
        'https://www.census.tracingthepast.org/index.php/en/minority-census/census-database/census-database?last_name=&first_name=&maiden_name=&place_of_birth=&street=&cck=minority_census&birth_year_for_search={}&city=Berlin&search=minority_census_search&task=search&start=0'.format(
            i))
    soup = BeautifulSoup(page.read(), 'html.parser')

    counter = soup.find(class_='counter')

    if counter is not None:
        print(soup.find(class_='counter').get_text())
        counter_from = re.findall(regex_counter, counter.get_text())[1]
        counter_start = 0

        for j in range(0, int(counter_from)):
            page = urlopen(
                'https://www.census.tracingthepast.org/index.php/en/minority-census/census-database/census-database?last_name=&first_name=&maiden_name=&place_of_birth=&street=&cck=minority_census&birth_year_for_search={}&city=Berlin&search=minority_census_search&task=search&start={}'.format(
                    i, counter_start))
            soup = BeautifulSoup(page.read(), 'html.parser')
            a_entries = soup.find_all(class_="popupbox")
            find_all_entries(a_entries)
            counter_start = counter_start + 25
    else:
        a_entries = soup.find_all(class_="popupbox")
        find_all_entries(a_entries)
