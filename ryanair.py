import datetime
import time

import redis

import session


class RyanairCrawler(object):
    BOGUS_URL = "https://www.ryanair.com/gb/en/booking/home/BCN/SXF/2018-11-02/2018-11-05/1/0/0/0"
    JSON_URL = "https://desktopapps.ryanair.com/v4/en-ie/availability"

    CUTOFF = 16

    def __init__(self):
        self.session = session.Session()
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)

    def crawl(self, dates, destination, origin):
        dates = self.create_date_list(dates)

        self.make_initial_request()

        for date in dates:
            beginning_of_key = self.get_key(date, origin, destination).encode()

            if not any(beginning_of_key in key for key in self.redis.keys()):
                json = self.make_json_request(date, origin, destination)
                self.parse_json(json)

    def create_date_list(self, dates):
        date_string = "%Y-%m-%d"
        day = datetime.datetime.strptime(dates[0], date_string)
        last_day = datetime.datetime.strptime(dates[1], date_string)

        day_range = [day.strftime(date_string)]

        while day < last_day:
            day += datetime.timedelta(6)
            day_range.append(day.strftime(date_string))

        return day_range

    @staticmethod
    def get_key(date, origin, destination, time=""):
        return date + origin + destination + time

    @property
    def headers(self):
        return {
            'origin': "https://www.ryanair.com",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "en-US,en;q=0.9",
            'user-agent': ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/68.0.3440.106 Safari/537.36"),
            'accept': "application/json, text/plain, */*",
            'authority': "desktopapps.ryanair.com",
            'cache-control': "no-cache",
        }

    def make_initial_request(self):
        response = self.session.get(
            self.BOGUS_URL,
            headers=self.headers
        )

        if not response.ok:
            raise Exception("Problem with initial request")

    def make_json_request(self, date, origin, destination):
        response = self.session.get(
            self.JSON_URL,
            headers=self.headers,
            params=self.params(origin, destination, date)
        )

        time.sleep(0.2)

        if not response.ok:
            raise Exception("Problem with JSON request")

        return response.json()

    def params(self, origin, destination, date):
        return {
            "ADT": "1",
            "CHD": "0",
            "DateIn": date,
            "DateOut": date,
            "Destination": destination,
            "FlexDaysIn": "6",
            "FlexDaysOut": "6",
            "INF": "0",
            "IncludeConnectingFlights": "true",
            "Origin": origin,
            "RoundTrip": "true",
            "TEEN": "0",
            "ToUs": "AGREED",
            "exists": "false",
        }

    def parse_json(self, json):
        # currency = json.get('currency')
        # server_time = json.get('serverTimeUTC')
        trips = json.get('trips', [])

        for trip in trips:
            destination = trip.get('destination')
            origin = trip.get('origin')
            # destination_name = trip.get('destinationName')
            # origin_name = trip.get('originName')

            dates = trip.get('dates', [])

            for date in dates:
                date_out = date.get('dateOut').split("T")[0]

                for flight in date.get('flights', []):
                    # duration = flight['duration']
                    fares_left = flight.get('faresLeft')

                    if fares_left:
                        price = flight['regularFare']['fares'][0]['amount']
                        departure, arrival = flight['segments'][0]['time']

                        departure_hour = departure.split("T")[1].rsplit(":", 1)[0]
                        # arrival_hour = arrival.split("T")[1].rsplit(":", 1)[0]

                        self.redis.set(
                            self.get_key(date_out,
                                         origin,
                                         destination,
                                         time=departure_hour),
                            price,
                        )

    def weekend(self):
        for key in self.redis.keys():
            key = key.decode()

            if key[0] != "w":
                date = datetime.datetime.fromisoformat(key[:10] + "T" + key[-5:] + ":00")

                origin = key[10:13]

                if origin == "BCN":
                    if date.strftime("%a") == 'Fri' and int(date.strftime("%H")) >= self.CUTOFF:
                        price = self.redis.get(key)
                        self.redis.set("w"+key, price)
                else:
                    if date.strftime("%a") == 'Sun' and int(date.strftime("%H")) >= self.CUTOFF:
                        price = self.redis.get(key)
                        self.redis.set("w"+key, price)
