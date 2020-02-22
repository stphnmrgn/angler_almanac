"""
Python:         2.7.10
Purpose         Aggregating freshwater fish harvest records with weather conditions
Author:         Stephen Morgan
"""

import urllib3
import json
import csv
import os
import time
import ephem
import datetime


# input csv file, harvest records of freshwater anglers
harvest = r"C:\Your\Data\Harvest\Harvests_scrubbed_DemoSample.csv"
# output csv file, aggregate harvest records and climatic variables
aggregate = r"C:\Your\Data\Created\Harvest_Weather_Aggregate\Harvest_WWO_aggregate_DemoSample.csv "


def createcsv(outputfile):
    # set variable to the output file pathway, used later to skip header
    file_exists = os.path.isfile(outputfile)
    with open(aggregate, 'ab') as f:
        w = csv.writer(f)
        header = ("date", "latitude", "longitude", "time", "uv_index", "cloud_cover",
                  "temp_f", "humidity", "wind_direction_degrees", "wind_speed_kmph",
                  "pressure_mb", "dewpoint_f", "head_index_f", "percipitation_mm",
                  "visualbility_km", "moon_phase", "dayofyear", "species", "angler",
                  "angler_id", "harvest_id")
        # if file exists, don't write header again
        if not file_exists:
            w.writerow(header)
        # return data from gethwc() and write to rows
        rows = gethwc(harvest)
        w.writerows(rows)


# get historical weather conditions
def gethwc(path):
    with open(harvest, 'rb') as csvfile:
        rcsv = csv.reader(csvfile, delimiter=',')
        # skip first row
        next(rcsv, None)

        for row in rcsv:
            date = row[0]
            lat = row[1]
            lon = row[2]
            utc = row[3]
            spp = row[8]  # species
            h_id = row[10]  # record id
            a_id = row[11]  # angler id
            angler = row[12]

            """Calculate Moon's illumination using utc values and ephem. Earth's moon 
            is a standard body in ephem. We ignore the "UTC" string in the utc field 
            (utc[:-3]) and pass it to ephem so it can compute the Moon's position 
            for each utc date. Ephem can return the moon's illumination or moon_phase 
            attribute using the moons position and utc date"""

            # calculate moon phase
            for i in utc:
                utcc = utc[:-3]  # ignore "UTC"
            m = ephem.Moon()
            m.compute(utcc)
            # moon phase, range [0,1]
            mp = m.moon_phase
            # calculate day of year, which is simply the x day out of 365
            dt = datetime.datetime.strptime(utcc[:-1], "%Y-%m-%d %H:%M:%S")
            # day of year, range [0, 365]
            dy = dt.timetuple().tm_yday

            """Use lat, long, & date to request API weather data for each harvest 
            record. The API requires dates to be yyyy-mm-dd, but our harvest records
            use yyyymmdd. Because CSVs suck balls, we have to break this down the 
            hard way -- splice the date field into three variables then combine them 
            back together to make the request"""

            for i in date:
                yyyy = date[0:4]  # isolate first four digits >> year
                mm = date[4:6]  # isolate 5th and 6th digit >> month
                dd = date[6:9]  # isolate 7th and 8th digit >> date

            # use PoolManager to make requests, bc thread safety
            http = urllib3.PoolManager()

            try:
                # request() returns HTTPResponse object.
                # Add json at end of url to return json data
                r = http.request('GET',
                                 'http://api.worldweatheronline.com/premium/v1/past-weather.ashx?key'
                                 '=_YOUR_KEY_HERE_&q=' + lat + ',' + lon + '&format=json&date=' +
                                 yyyy + '-' + mm + '-' + dd + '&tp=24')
            except urllib3.exceptions.HTTPError as e:
                print "HTTP error:              ", e
                break

            print "Request Time:        ", time.clock()

            """To get climate data, we first need to know what keys & the dictionary 
            the keys are within. Using the print statement parsed_json/jsondata we
            determined the keys & dictionaries the climate data are stored:
            The key "data" contains key "weather" which contains a dictionary [] 
            that contains the key "date""""

            # response = r.status #<<<---commented out, return http response code
            jsondata = r.data  # return json data
            parsed_json = json.loads(jsondata.decode('utf-8'))
            # return the first key in response body
            body = parsed_json['data']

            # some harvest dates aren't in API and return error
            if "error" in body:
                print "Warning:              " + \
                    parsed_json['data']['error'][0]['msg']
                # error message when we reach our rquest limit/day
                limit_error = "API key has reached calls per day allowed limit."
                # if we max out our limit, break the loop and end program
                # if no data/error, then only yeild three fields
                if limit_error in body:
                    break
                else:
                    seq = (date, lat, lon)
                    yield seq
            else:
                date1 = parsed_json['data']['weather'][0]['date']
                print "Harvest Date:        ", yyyy + '-' + mm + '-' + dd
                print "Json Date:           ", date1
                # UV index, percent, range [0, 100]
                uv = parsed_json['data']['weather'][0]['uvIndex']
                # cloud cover, percent, [0, 100]
                cc = parsed_json['data']['weather'][0]['hourly'][0]['cloudcover']
                # humidity, percent, [0, 100]
                hu = parsed_json['data']['weather'][0]['hourly'][0]['humidity']
                # precipitation, mm, [0, max]
                precip = parsed_json['data']['weather'][0]['hourly'][0]['precipMM']
                # air pressure, millibar, [min, max]
                ap = parsed_json['data']['weather'][0]['hourly'][0]['pressure']
                # dewpoint, Fahrenheit, [min, max]
                dew = parsed_json['data']['weather'][0]['hourly'][0]['DewPointF']
                # head index, Fahrenheit, [min, max]
                hi = parsed_json['data']['weather'][0]['hourly'][0]['HeatIndexF']
                # temperature, Fahrenheit, [min, max]
                temp = parsed_json['data']['weather'][0]['hourly'][0]['tempF']
                # visibility, km, [0, max]
                viz = parsed_json['data']['weather'][0]['hourly'][0]['visibility']
                # wind direction, degrees, [0, 360]
                wd = parsed_json['data']['weather'][0]['hourly'][0]['winddirDegree']
                # wind speed, km/hour, [0, max]
                ws = parsed_json['data']['weather'][0]['hourly'][0]['windspeedKmph']

                """Organize the copied, computed, and retrieved data into the same sequence 
                as the headers of createcsv(), then return them all so they can be used
                to populate a new csv."""

                seq = (date, lat, lon, utc, uv, cc, temp, hu, wd, ws, ap,
                       dew, hi, precip, viz, mp, dy, spp, angler, a_id, h_id)

                yield seq

            # sleep in order to limit rate of requests to API
            print "\nNap Time:            ", time.clock()
            time.sleep(6)
            print "\n"

    # close harvest records
    csvfile.close()


if __name__ == '__main__':
    createcsv(aggregate)
    gethwc(harvest)

print "\nValar Morghulis"
