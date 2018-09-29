import datetime
import logging
import time

import redis

import session


def combined_price(weekend):
    return [weekend[0].price + return_flight.price for return_flight in weekend[1:]]


class Flight(object):
    def __init__(self, key, value):
        key = key.decode()

        self.date = datetime.datetime.fromisoformat(key[:10] + "T" + key[-5:] + ":00")
        self.origin = key[10:13]
        self.destination = key[13:16]
        self.price = float(value.decode())


class RyanairCrawler(object):
    BOGUS_URL = "https://www.ryanair.com/gb/en/booking/home/BCN/SXF/2018-11-02/2018-11-05/1/0/0/0"
    JSON_URL = "https://desktopapps.ryanair.com/v4/en-ie/availability"

    CUTOFF_FRIDAY = 16
    CUTOFF_THURSDAY = 16
    CUTOFF_RETURN = 16

    def __init__(self):
        self.session = session.Session()
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)

    def crawl(self, dates, destination, origin):
        dates = self.create_date_list(dates)

        self.make_initial_request()

        for date in dates:
            beginning_of_key = self.get_key(date, origin, destination).encode()

            if not any(beginning_of_key in key for key in self.redis.keys()):
                try:
                    json = self.make_json_request(date, origin, destination)
                    logging.info("Scraped %s for %s-%s trip",
                                 date, origin, destination)
                    self.parse_json(json)
                except Exception as e:
                    logging.warning("Something's wrong: %s", e)

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

    def import_from_redis(self):
        keys = self.redis.keys()
        weekend_keys = filter(lambda key: key.decode()[0] != "w", keys)
        flights = []

        for key in weekend_keys:
            flights.append(Flight(key, self.redis.get(key)))

        return flights

    def match(self, begin, end):
        conditions = [
            datetime.timedelta(0) < (end.date - begin.date) <= datetime.timedelta(5),
            begin.destination == end.origin,
        ]
        return True if all(conditions) else False

    def make_initial_request(self):
        response = self.session.get(
            self.BOGUS_URL,
            headers=self.headers
        )

        if not response or not response.ok:
            raise Exception("Problem with initial request")

    def make_json_request(self, date, origin, destination):
        response = self.session.get(
            self.JSON_URL,
            headers=self.headers,
            params=self.params(origin, destination, date)
        )

        time.sleep(0.2)

        if not response or not response.ok:
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
        trips = json.get('trips', [])

        for trip in trips:
            destination = trip.get('destination')
            origin = trip.get('origin')

            dates = trip.get('dates', [])

            for date in dates:
                date_out = date.get('dateOut').split("T")[0]

                for flight in date.get('flights', []):
                    fares_left = flight.get('faresLeft')

                    if fares_left:
                        price = flight['regularFare']['fares'][0]['amount']
                        departure, arrival = flight['segments'][0]['time']

                        departure_hour = departure.split("T")[1].rsplit(":", 1)[0]

                        self.redis.set(
                            self.get_key(date_out,
                                         origin,
                                         destination,
                                         time=departure_hour),
                            price,
                        )

    def weekend_begin_condition(self, flight, variant):
        conditions = [flight.origin == "BCN"]
        if variant == 0:
            conditions.extend([
                flight.date.strftime("%a") == 'Fri',
                int(flight.date.strftime("%H")) >= self.CUTOFF_FRIDAY
            ])
        elif variant == 1:
            conditions.extend([
                flight.date.strftime("%a") == 'Thu',
                int(flight.date.strftime("%H")) >= self.CUTOFF_THURSDAY
            ])
        elif variant == 2:
            conditions.extend([
                flight.date.strftime("%a") == 'Fri',
                int(flight.date.strftime("%H")) >= self.CUTOFF_FRIDAY
            ])
        return all(conditions)

    def weekend_end_condition(self, flight, variant):
        conditions = [int(flight.date.strftime("%H")) >= self.CUTOFF_RETURN,
                      flight.origin != "BCN"]
        if variant == 0:
            conditions.append(flight.date.strftime("%a") == 'Sun')
        elif variant == 1:
            conditions.append(flight.date.strftime("%a") == 'Sun')
        elif variant == 2:
            conditions.append(flight.date.strftime("%a") == 'Mon')
        return all(conditions)

    def weekend_organizer(self, flights, variant=0):
        weekend_beginnings = filter(
            lambda flight: self.weekend_begin_condition(flight, variant),
            flights,
        )
        weekend_ends = list(filter(
            lambda flight: self.weekend_end_condition(flight, variant),
            flights,
        ))
        weekends = []

        for flight in weekend_beginnings:
            weekends.append([flight])

            for return_flight in weekend_ends:
                if self.match(flight, return_flight):
                    weekends[-1].append(return_flight)

        return sorted(
            filter(lambda weekend: len(weekend) > 1, weekends),
            key=combined_price
        )
