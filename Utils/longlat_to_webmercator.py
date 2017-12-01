"""
Quick and dirty script to convert the Longitude and Latitude values into webmercator values
"""


import pandas as pd
import datashader

import time
import logging
import sqlite3

import argparse

parser = argparse.ArgumentParser(description='Get geodata from adresses')
parser.add_argument('-begin', '-f', type=int, required=True)
parser.add_argument('-end', '-t', type=int, required=True)

conn = sqlite3.connect("adresses_31.db")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

args = parser.parse_args()

df = pd.read_sql('SELECT * FROM census_2 WHERE Longitude IS NOT NULL', conn)
adresses = df.to_dict()

# letzter wert 8500
# insgesamt 72212
for number in range(args.begin, len(df)):
    try:
        logger.info("Try to get data for Nummer: {}".format(number))
        logger.info(adresses['adresse'][number])
        # try to geocode using a service
        location = datashader.utils.lnglat_to_meters(float(adresses['Longitude'][number]), float(adresses['Latitude'][number]))

        # if it returns a location
        if location is not None:
            logger.info("Insert into db: x_mercator: {}, y_mercartor: {}".format(location[0], location[1]))
            with conn:
                cur = conn.cursor()
                cur.execute(
                    'UPDATE census_2 SET x_mercator_census = {}, y_mercator_census = {} WHERE "index" = {}'.format(location[0],
                                                                                                          location[1], adresses['index'][number]))
            cur.close()

    except Exception as e:
        print(e)
        logger.error("Last number: {}".format(number))
        exit(0)
