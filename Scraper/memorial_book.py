"""
Quick and dirty scraper to get the data from the memorial book.

Used a little hack to make this script easier. The former scraper had the issue
to lose the values from the jQuery during page iteration. So I manipulated the jQuery
in the console to get all entries from berlin and used BeautifulSoup to get all links.

This scraper script iterates over the links and parses the data directly into the sqlite database

TODO: regex and database column names could be better
"""

from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import sqlite3
import pandas as pd

regex_geburtsdatum = r"(?<=geboren am\s)\d*\.\s?\w*\s?\d*"
regex_geburtsort = r"(?<=\d\d\d\d\sin\s)\w*"
regex_todesdatum = r"(?<=Todesdatum:\s)\d*\.\s?\w*\s?\d*"
regex_todesort = r"(?<=Todesort:\s).*"
regex_deportationsstart = r"(?<=ab\s)\w*"
regex_deportationszeitpunkt = r"\d+\.\s\w+\s\d+"
regex_deportationsziel = r"(?<=\d\d\d\d\,\s)\w*"
regex_test_datum = r"\d{4}"
regex_get_haft = r"(?<=\d{4}\,\s).+"
regex_get_haft_date = r"^(.+?),"
regex_haft_ohne_datum = r".+"

conn = sqlite3.connect("adresses_31.db")

df = pd.read_sql('SELECT * FROM links', conn)
links = df['Links'].values.tolist()


def insert_to_db(entries):
    c = conn.cursor()
    c.execute("INSERT INTO memorial_book (vorname, nachname, geburtsdatum, geburtsort, inhaftierung, deportationsstart,"
              " deportationsziel, deportationsdatum, weitere_deportation, weitere_deportation_zeitpunkt, todesdatum,"
              " todesort, emigration, id, link, deportation_3, deportation_3_zeitpunkt, deportation_4,"
              " deportation_4_zeitpunkt, inhaftierung_1, inhaftierung_1_zeitpunkt, inhaftierung_2, inhaftierung_2_zeitpunkt"
              ", inhaftierung_3, inhaftierung_3_zeitpunkt, inhaftierung_4, inhaftierung_4_zeitpunkt, emigration_1,"
              " emigration_1_zeitpunkt, emigration_2, emigration_2_zeitpunkt, emigration_3, emigration_3_zeitpunkt,"
              " emigration_4, emigration_4_zeitpunkt"") VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}', '{}', '{}', '{}', '{}', '{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(
        entries['Vorname'],
        entries['Nachname'],
        entries['Geburtsdatum'],
        entries['Geburtsort'],
        entries['Inhaftierung'],
        entries[
            'Deportationsstart'],
        entries[
            'Deportationsziel'],
        entries[
            'Deportationszeitpunkt'],
        entries[
            'Weitere_Deportation'],
        entries[
            'Weitere_Deportation_Zeitpunkt'],
        entries['Todesdatum'],
        entries['Todesort'],
        entries['Emigration'], entries['ID'], entries['Link'], entries['Deportation_3'],
        entries['Deportation_3_Zeitpunkt'], entries['Deportation_4'], entries['Deportation_4_Zeitpunkt'],
        entries['Inhaftierung_1'], entries['Inhaftierung_1_Zeitpunkt'], entries['Inhaftierung_2'],
        entries['Inhaftierung_2_Zeitpunkt'], entries['Inhaftierung_3'], entries['Inhaftierung_3_Zeitpunkt'],
        entries['Inhaftierung_4'], entries['Inhaftierung_4_Zeitpunkt'], entries['Emigration_1'],
        entries['Emigration_1_Zeitpunkt'], entries['Emigration_2'], entries['Emigration_2_Zeitpunkt'],
        entries['Emigration_3'], entries['Emigration_3_Zeitpunkt'], entries['Emigration_4'],
        entries['Emigration_4_Zeitpunkt']))
    conn.commit()


# range are the links in total
for i in range(0, 60325):
    page = urlopen(links[i])
    # page = urlopen('https://www.bundesarchiv.de/gedenkbuch/de880631')
    soup = BeautifulSoup(page.read(), 'html.parser')
    print(links[i])
    print("ID: {}".format(i))
    try:
        print(soup.find(class_="rowTypeB").get_text())
        names = soup.find(class_="rowTypeB").get_text().split(',')
    except AttributeError:
        print(soup.find(class_="rowTypeA").get_text())
        names = soup.find(class_="rowTypeA").get_text().split(',')

    dict_to_insert = {'Vorname': names[1], 'Nachname': names[0], 'Geburtsdatum': None, 'Geburtsort': None,
                      'Inhaftierung': None, 'Deportationsziel': None, 'Deportationszeitpunkt': None,
                      'Deportationsstart': None, 'Weitere_Deportation': None, 'Weitere_Deportation_Zeitpunkt': None,
                      'Deportation_3': None, 'Deportation_3_Zeitpunkt': None, 'Deportation_4': None,
                      'Deportation_4_Zeitpunkt': None, 'Inhaftierung_1': None, 'Inhaftierung_1_Zeitpunkt': None,
                      'Inhaftierung_2': None, 'Inhaftierung_2_Zeitpunkt': None, 'Inhaftierung_3': None,
                      'Inhaftierung_3_Zeitpunkt': None, 'Inhaftierung_4': None, 'Inhaftierung_4_Zeitpunkt': None,
                      'Todesdatum': None, 'Todesort': None, 'Emigration': None, 'Emigration_1': None,
                      'Emigration_1_Zeitpunkt': None, 'Emigration_2': None, 'Emigration_2_Zeitpunkt': None,
                      'Emigration_3': None, 'Emigration_3_Zeitpunkt': None, 'Emigration_4': None,
                      'Emigration_4_Zeitpunkt': None, 'Link': links[i], 'ID': i}

    # The data is way to inconsistent, misses are possible
    for entry in soup.find_all(class_="leftIndent"):
        entry_str = "Entry: {} \n".format(entry.get_text(separator=" | "))
        print(entry_str)
        if "geboren am" in entry_str:
            geburtsort = re.findall(regex_geburtsort, entry_str)
            geburtsdatum = re.findall(regex_geburtsdatum, entry_str)
            if len(geburtsdatum) > 0:
                dict_to_insert['Geburtsdatum'] = geburtsdatum[0]
            if len(geburtsort) > 0:
                dict_to_insert['Geburtsort'] = geburtsort[0]
        elif "Inhaftierung" in entry_str:
            # print(entry_str.split('|'))
            haft = entry_str.split('|')
            # print(len(entry_str.split('|')))
            counter_t = 1
            counter_f = 1
            for j in range(1, len(haft)):
                if re.search(regex_test_datum, haft[j]):
                    haft_date = re.findall(regex_get_haft_date, haft[j])
                    if len(haft_date) > 0:
                        # print('Inhaftierungsdatum: {}'.format(haft_date[0]))
                        if counter_t == 1:
                            dict_to_insert['Inhaftierung_1_Zeitpunkt'] = haft_date[0].strip()
                        elif counter_t == 2:
                            dict_to_insert['Inhaftierung_2_Zeitpunkt'] = haft_date[0].strip()
                        elif counter_t == 3:
                            dict_to_insert['Inhaftierung_3_Zeitpunkt'] = haft_date[0].strip()
                        elif counter_t == 4:
                            dict_to_insert['Inhaftierung_4_Zeitpunkt'] = haft_date[0].strip()
                        counter_t = counter_t + 1
                    if 'Deportation' in haft[j] or 'Emigration' in haft[j]:
                        break
                    else:
                        haft_entry = re.findall(regex_get_haft, haft[j])
                        if len(haft_entry) > 0:
                            # print('Haft: {}'.format(haft_entry[0]))
                            # print(counter_f)
                            if counter_f == 1:
                                dict_to_insert['Inhaftierung_1'] = haft_entry[0].strip()
                            elif counter_f == 2:
                                dict_to_insert['Inhaftierung_2'] = haft_entry[0].strip()
                            elif counter_f == 3:
                                dict_to_insert['Inhaftierung_3'] = haft_entry[0].strip()
                            elif counter_f == 4:
                                dict_to_insert['Inhaftierung_4'] = haft_entry[0].strip()

                            counter_f = counter_f + 1
                else:
                    if 'Deportation' in haft[j] or 'Emigration' in haft[j]:
                        break
                    else:
                        haft_entry = re.findall(regex_haft_ohne_datum, haft[j])
                        if len(haft_entry) > 0:
                            # print('Haft: {}'.format(haft_entry[0]))
                            # print(counter_f)
                            if counter_f == 1:
                                dict_to_insert['Inhaftierung_1'] = haft_entry[0].strip()
                            elif counter_f == 2:
                                dict_to_insert['Inhaftierung_2'] = haft_entry[0].strip()
                            elif counter_f == 3:
                                dict_to_insert['Inhaftierung_3'] = haft_entry[0].strip()
                            elif counter_f == 4:
                                dict_to_insert['Inhaftierung_4'] = haft_entry[0].strip()
                            counter_f = counter_f + 1

            dict_to_insert['Inhaftierung'] = True
        elif "Deportation" in entry_str:
            # print(entry_str)
            deport = entry_str.split('|')
            # print(deport)
            counter_t = 1
            counter_f = 1
            if len(deport) > 0:
                deportationsstart = re.findall(regex_haft_ohne_datum, deport[1])
                if len(deportationsstart) > 0:
                    dict_to_insert['Deportationsstart'] = deportationsstart[0].strip()
            for k in range(2, len(entry_str.split('|'))):
                if re.search(regex_test_datum, deport[k]):
                    deportationsziel = re.findall(regex_get_haft, deport[k])
                    deportationszeitpunkt = re.findall(regex_get_haft_date, deport[k])
                    if len(deportationszeitpunkt) > 0:
                        # print(deportationszeitpunkt[0].strip())
                        # print(counter_f)
                        if counter_f == 1:
                            dict_to_insert['Deportationszeitpunkt'] = deportationszeitpunkt[0].strip()
                        elif counter_f == 2:
                            dict_to_insert['Weitere_Deportation_Zeitpunkt'] = deportationszeitpunkt[0].strip()
                        elif counter_f == 3:
                            dict_to_insert['Deportation_3_Zeitpunkt'] = deportationszeitpunkt[0].strip()
                        elif counter_f == 4:
                            dict_to_insert['Deportation_4_Zeitpunkt'] = deportationszeitpunkt[0].strip()
                        counter_f = counter_f + 1
                    if len(deportationsziel) > 0:
                        # print(deportationsziel[0].strip())
                        # print(counter_t)
                        if counter_t == 1:
                            dict_to_insert['Deportationsziel'] = deportationsziel[0].strip()
                        elif counter_t == 2:
                            dict_to_insert['Weitere_Deportation'] = deportationsziel[0].strip()
                        elif counter_t == 3:
                            dict_to_insert['Deportation_3'] = deportationsziel[0].strip()
                        elif counter_t == 4:
                            dict_to_insert['Deportation_4'] = deportationsziel[0].strip()
                        counter_t = counter_t + 1
                else:
                    deportationsziel = re.findall(regex_haft_ohne_datum, deport[k])
                    if len(deportationsziel) > 0:
                        # print(deportationsziel[0].strip())
                        # print(counter_t)
                        if counter_t == 1:
                            dict_to_insert['Deportationsziel'] = deportationsziel[0].strip()
                        elif counter_t == 2:
                            dict_to_insert['Weitere_Deportation'] = deportationsziel[0].strip()
                        elif counter_t == 3:
                            dict_to_insert['Deportation_3'] = deportationsziel[0].strip()
                        elif counter_t == 4:
                            dict_to_insert['Deportation_4'] = deportationsziel[0].strip()
                        counter_t = counter_t + 1

        elif "Todesort" in entry_str:
            todesort = re.findall(regex_todesort, entry_str)
            todesdatum = re.findall(regex_todesdatum, entry_str)
            if len(todesdatum) > 0:
                dict_to_insert['Todesdatum'] = todesdatum[0]
            if len(todesort) > 0:
                dict_to_insert['Todesort'] = todesort[0]
        elif "Emigration" in entry_str:
            # print(entry_str)
            emi = entry_str.split('|')
            counter_t = 1
            counter_f = 1
            for l in range(1, len(emi)):
                if re.search(regex_test_datum, emi[l]):
                    emi_date = re.findall(regex_get_haft_date, emi[l])
                    if len(emi_date) > 0:
                        # print('Emigrationsdatum: {}'.format(emi_date[0].strip()))
                        # print(counter_t)
                        if counter_t == 1:
                            dict_to_insert['Emigration_1_Zeitpunkt'] = emi_date[0].strip()
                        elif counter_t == 2:
                            dict_to_insert['Emigration_2_Zeitpunkt'] = emi_date[0].strip()
                        elif counter_t == 3:
                            dict_to_insert['Emigration_3_Zeitpunkt'] = emi_date[0].strip()
                        elif counter_t == 4:
                            dict_to_insert['Emigration_4_Zeitpunkt'] = emi_date[0].strip()
                        counter_t = counter_t + 1

                    emi_entry = re.findall(regex_get_haft, emi[l])
                    if len(emi_entry) > 0:
                        # print('Emigration: {}'.format(emi_entry[0]))
                        # print(counter_f)
                        if counter_f == 1:
                            dict_to_insert['Emigration_1'] = emi_entry[0].strip()
                        elif counter_f == 2:
                            dict_to_insert['Emigration_2'] = emi_entry[0].strip()
                        elif counter_f == 3:
                            dict_to_insert['Emigration_3'] = emi_entry[0].strip()
                        elif counter_f == 4:
                            dict_to_insert['Emigration_4'] = emi_entry[0].strip()
                        counter_f = counter_f + 1
                else:
                    emi_entry = re.findall(regex_haft_ohne_datum, emi[l])
                    if len(emi_entry) > 0:
                        # print('Emigration: {}'.format(emi_entry[0]))
                        # print(counter_f)
                        if counter_f == 1:
                            dict_to_insert['Emigration_1'] = emi_entry[0].strip()
                        elif counter_f == 2:
                            dict_to_insert['Emigration_2'] = emi_entry[0].strip()
                        elif counter_f == 3:
                            dict_to_insert['Emigration_3'] = emi_entry[0].strip()
                        elif counter_f == 4:
                            dict_to_insert['Emigration_4'] = emi_entry[0].strip()
                        counter_f = counter_f + 1
            dict_to_insert['Emigration'] = True
        else:
            print("empty")

    print(dict_to_insert)
    insert_to_db(dict_to_insert)
conn.close()
