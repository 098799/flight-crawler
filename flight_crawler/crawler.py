import datetime
import logging
import time

from flight_crawler import constants
from flight_crawler import redis_entity
from flight_crawler import session

import requests


class Crawler(redis_entity.RedisEntity):
    SLEEP_TIME = 0.2

    def __init__(self):
        super().__init__()
        self.session = session.Session()

    def crawl(self, begin, end, destination, origin):
        """Main entry point for the bot."""
        dates = self.create_date_list(begin, end)

        for date in dates:
            json = self.make_json_request(date, origin, destination)

            if json:
                logging.info("Scraped %s for %s-%s trip", date, origin, destination)
                return self.parse_json(json)

    def crawl_wrapper(self, *args, **kwargs):
        """Perform the crawl and set appropriate data in redis for future use."""
        results = self.crawl(*args, **kwargs)

        for redis_key, price in results.items():
            self.redis.set(redis_key, price)

    def create_date_list(self, begin, end):
        """Generate a list of dates to be used in an API request."""
        return [begin + datetime.timedelta(day) for day in range(0, (end - begin).days, 6)]

    def currency_exchange(self, currency):
        """Convert currency dynamically if Ryanair shows something that's not EUR."""
        if not self.redis.get(currency):
            response = requests.get(constants.CURRENCY_URL.format(currency))
            multiplier = response.json().get(f"EUR_{currency}", {}).get("val")
            self.redis.set(currency, multiplier)

        return multiplier

    def json_request_params(self, origin, destination, date):
        date_string = date.isoformat()
        return {
            **constants.PARAMS,
            "DateIn": date_string,
            "DateOut": date_string,
            "Destination": destination,
            "Origin": origin,
        }

    def make_json_request(self, date, origin, destination):
        response = self.session.get(
            constants.JSON_URL, headers=constants.HEADERS, params=self.json_request_params(origin, destination, date)
        )

        time.sleep(self.SLEEP_TIME)

        if response.ok:
            return response.json()

    def parse_json(self, json):
        results = {}

        trips = json.get("trips", [])
        currency = json.get("currency")

        for trip in trips:
            destination = trip.get("destination")
            origin = trip.get("origin")

            dates = trip.get("dates", [])

            for date in dates:
                date_out = date.get("dateOut").split("T")[0]

                for flight_list in date.get("flights", []):
                    fares_left = flight_list.get("faresLeft")

                    if fares_left:
                        price = flight_list["regularFare"]["fares"][0]["amount"]

                        if currency != "EUR":
                            price = price / self.currency_exchange(currency)

                        departure, arrival = flight_list["segments"][0]["time"]

                        departure_hour = departure.split("T")[1].rsplit(":", 1)[0]

                        results[self.redis_flight_key(date_out, origin, destination, time=departure_hour)] = price

        return results

    @staticmethod
    def redis_flight_key(date, origin, destination, time=""):
        return date + origin + destination + time
