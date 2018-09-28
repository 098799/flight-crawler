import datetime
import requests
import time


class RyanairCrawler(object):
    BOGUS_URL = "https://www.ryanair.com/gb/en/booking/home/BCN/SXF/2018-11-02/2018-11-05/1/0/0/0"
    JSON_URL = "https://desktopapps.ryanair.com/v4/en-ie/availability"

    def __init__(self):
        self.session = requests.session()

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

    def params(self, origin, destination, date):
        return {
            "ADT": "1",
            "CHD": "0",
            # "DateIn": self.date_in,
            "DateOut": date,
            "Destination": destination,
            "FlexDaysIn": "0",
            "FlexDaysOut": "0",
            "INF": "0",
            "IncludeConnectingFlights": "true",
            "Origin": origin,
            "RoundTrip": "false",
            "TEEN": "0",
            "ToUs": "AGREED",
            "exists": "false",
        }

    def crawl(self, dates, destination=None, origin=None):
        dates = self.create_date_list(dates)

        self.make_initial_request()
        output = {}

        for date in dates:
            json = self.make_json_request(origin, destination, date)
            flight, results = self.parse_json(json)
            output[date] = results
            time.sleep(0.1)

        return flight, output

    def create_date_list(self, dates):
        date_string = "%Y-%m-%d"
        day = datetime.datetime.strptime(dates[0], date_string)
        last_day = datetime.datetime.strptime(dates[1], date_string)

        day_range = [day.strftime(date_string)]

        while day != last_day:
            day += datetime.timedelta(1)
            day_range.append(day.strftime(date_string))

        return day_range

    def make_initial_request(self):
        response = self.session.get(
            self.BOGUS_URL,
            headers=self.headers
        )

        if not response.ok:
            raise Exception("Problem with initial request")

    def make_json_request(self, origin, destination, date):
        response = self.session.get(
            self.JSON_URL,
            headers=self.headers,
            params=self.params(origin, destination, date)
        )

        if not response.ok:
            raise Exception("Problem with JSON request")

        return response.json()

    def parse_json(self, json):
        output = []

        currency = json.get('currency')
        trips = json.get('trips')

        for trip in trips:
            destination = trip.get('destination')
            origin = trip.get('origin')

            destination_name = trip.get('destinationName')
            origin_name = trip.get('originName')

            for flight in trip['dates'][0]['flights']:
                duration = flight['duration']
                price = flight['regularFare']['fares'][0]['amount']
                departure, arrival = flight['segments'][0]['time']

                departure_hour = departure.split("T")[1].rsplit(":", 1)[0]
                arrival_hour = arrival.split("T")[1].rsplit(":", 1)[0]

                output.append(
                    {
                        'duration': duration,
                        'price': f"{price} {currency}",
                        'departure': departure_hour,
                        'arrival': arrival_hour,
                    }
                )

        return f"{origin_name} -> {destination_name}", output
