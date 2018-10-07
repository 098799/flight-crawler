import datetime
import logging
import time

from flight_crawler import flight
from flight_crawler import session
from flight_crawler import utils

import redis

import requests


class Crawler(object):
    BOGUS_URL = "https://www.ryanair.com/gb/en/booking/home/BCN/SXF/2018-11-02/2018-11-05/1/0/0/0"
    CURRENCY_URL = "http://free.currencyconverterapi.com/api/v5/convert?q=EUR_{}&compact=y"
    JSON_URL = "https://desktopapps.ryanair.com/v4/en-ie/availability"

    CUTOFF_FRIDAY = 16
    CUTOFF_THURSDAY = 16
    CUTOFF_RETURN = 16

    HOW_MANY_FLIGHTS_TO_SHOW = 1

    def __init__(self):
        self.session = session.Session()
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        self._currency_exchange = {}

    def crawl(self, dates, destination, origin):
        dates = self.create_date_list(dates)

        self.make_initial_request()

        for date in dates:
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

    def currency_exchange(self, currency):
        if not self._currency_exchange.get('currency'):
            response = requests.get(self.CURRENCY_URL.format(currency))
            multiplier = response.json().get(f'EUR_{currency}', {}).get('val')
            self._currency_exchange[currency] = multiplier

        return self._currency_exchange.get(currency)

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
            flights.append(flight.Flight(key, self.redis.get(key)))

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
        currency = json.get('currency')

        if currency != "EUR":
            multiplier = self.currency_exchange(currency)

        for trip in trips:
            destination = trip.get('destination')
            origin = trip.get('origin')

            dates = trip.get('dates', [])

            for date in dates:
                date_out = date.get('dateOut').split("T")[0]

                for flight_list in date.get('flights', []):
                    fares_left = flight_list.get('faresLeft')

                    if fares_left:
                        price = flight_list['regularFare']['fares'][0]['amount']

                        if currency != "EUR":
                            price = price / multiplier

                        departure, arrival = flight_list['segments'][0]['time']

                        departure_hour = departure.split("T")[1].rsplit(":", 1)[0]

                        self.redis.set(
                            self.get_key(date_out,
                                         origin,
                                         destination,
                                         time=departure_hour),
                            price,
                        )

    def weekend_begin_condition(self, flight_list, variant):
        conditions = [flight_list.origin == "BCN"]
        if variant == 0:
            conditions.extend([
                flight_list.date.strftime("%a") == 'Fri',
                int(flight_list.date.strftime("%H")) >= self.CUTOFF_FRIDAY
            ])
        elif variant == 1:
            conditions.extend([
                flight_list.date.strftime("%a") == 'Thu',
                int(flight_list.date.strftime("%H")) >= self.CUTOFF_THURSDAY
            ])
        elif variant == 2:
            conditions.extend([
                flight_list.date.strftime("%a") == 'Fri',
                int(flight_list.date.strftime("%H")) >= self.CUTOFF_FRIDAY
            ])
        return all(conditions)

    def weekend_end_condition(self, flight_list, variant):
        conditions = [int(flight_list.date.strftime("%H")) >= self.CUTOFF_RETURN,
                      flight_list.origin != "BCN"]
        if variant == 0:
            conditions.append(flight_list.date.strftime("%a") == 'Sun')
        elif variant == 1:
            conditions.append(flight_list.date.strftime("%a") == 'Sun')
        elif variant == 2:
            conditions.append(flight_list.date.strftime("%a") == 'Mon')
        return all(conditions)

    def weekend_organizer(self, flights, variant=0):
        weekend_beginnings = filter(
            lambda flight_list: self.weekend_begin_condition(flight_list, variant),
            flights,
        )
        weekend_ends = list(filter(
            lambda flight_list: self.weekend_end_condition(flight_list, variant),
            flights,
        ))
        weekends = []

        for flight_ in weekend_beginnings:
            weekends.append([flight_])

            for return_flight in weekend_ends:
                if self.match(flight_, return_flight):
                    weekends[-1].append(return_flight)

        sorted_weekends = sorted(
            filter(lambda weekend: len(weekend) > 1, weekends),
            key=utils.combined_price
        )

        destinations = {flight[0].destination for flight in sorted_weekends}

        return_list = []

        for destination in destinations:
            for weekend in sorted_weekends:
                if weekend[0].destination == destination and len(list(filter(
                        lambda w: w[0].destination == destination, return_list
                ))) < self.HOW_MANY_FLIGHTS_TO_SHOW:
                    return_list.append(weekend)

        return sorted(return_list, key=utils.combined_price)
