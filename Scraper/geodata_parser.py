"""
Main script for getting geodata from the provided addresses. Can easily be changed for different tables in the database

Use arguments to provide start, end and the provider

Info: Although OpenMapQuest was added, the API doesn't seem to work. Google is the fastest provider for the geomapping,
 but the error rate in getting totally wrong data is fairly high. Nominatim is slower but is way more precise.
"""

import pandas as pd
import time
import logging
import sqlite3

import argparse

from geopy.geocoders import GoogleV3
from geopy.geocoders import Nominatim
from geopy.geocoders import OpenMapQuest

parser = argparse.ArgumentParser(description='Get geodata from adresses')
parser.add_argument('-begin', '-f', type=int, required=True)
parser.add_argument('-end', '-t', type=int, required=True)
parser.add_argument('-geo', '-g', required=True)

conn = sqlite3.connect("adresses_31.db")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

geolocator = None

args = parser.parse_args()
if args.geo == 'google':
    geolocator = GoogleV3(api_key='Your API key', timeout=2)
elif args.geo == 'osm':
    geolocator = Nominatim(timeout=30)
elif args.geo == 'mapquest':
    geolocator = OpenMapQuest(api_key='Your Api key')

df = pd.read_csv('census.csv', sep=';')
adresses = df.to_dict()

# insgesamt 72212
for number in range(args.begin, args.end):
    try:
        time.sleep(1)
        logger.info("Try to get data for Nummer: {}".format(number))
        logger.info(adresses['adresse'][number])
        # try to geocode using a service
        location = geolocator.geocode("{}, Berlin".format(adresses['adresse'][number]))

        # if it returns a location
        if location is not None:
            number = number + 1
            logger.info(location.address)
            logger.info("Insert into db: Longitude: {}, Latitude: {}".format(location.longitude, location.latitude))
            with conn:
                cur = conn.cursor()
                cur.execute(
                    'UPDATE main.census SET Longitude = {}, Latitude = {}, census_geocode = \"{}\" WHERE ROWID = {}'.format(
                        location.longitude, location.latitude, location.address, number))
                cur.close()
        else:
            logger.warning("Keine Geodaten gefunden für {}".format(adresses['adresse'][number]))
            number = number + 1
            with conn:
                cur = conn.cursor()
                logger.info("UPDATE main.adress31 SET Longitude = {}, Latitude = {} WHERE ROWID = {}".format("Null", "Null",
                                                                                                               number))
                cur.execute("UPDATE main.adress31 SET Longitude = {}, Latitude = {} WHERE ROWID = {}".format("Null", "Null",
                                                                                                               number))
                cur.close()
    except Exception as e:
        print(e)
        logger.error("Last number: {}".format(number))
        exit(0)
