import argparse
import datetime
import logging

from flight_crawler import crawler
from flight_crawler import utils
from flight_crawler import weekend

import tabulate


def isoformat_date(date_string):
    try:
        return datetime.date.fromisoformat(date_string)
    except ValueError:
        msg = f"{date_string} is not a valid date string"
        raise argparse.ArgumentTypeError(msg)


def crawl():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("begin", help="Date for the beginning of search in format YYYY-MM-DD", type=isoformat_date)
    parser.add_argument("end", help="Date for the end of search in format YYYY-MM-DD", type=isoformat_date)
    parser.add_argument("origin", help="3 letter code for the origin airport", type=str)
    parser.add_argument("destination", help="3 letter code for the destination airport", type=str)

    cli_args = parser.parse_args()

    bot = crawler.Crawler()

    bot.crawl_wrapper(cli_args.begin, cli_args.end, origin=cli_args.origin, destination=cli_args.destination)


def calculate_weekend():
    def table(weekends, stations):
        table = []

        for weekend_ in weekends:
            destination = stations[weekend[0].destination]["name"]
            date = weekend[0].date
            price = utils.combined_price(weekend)
            table.append([destination, date, price])

        return table

    parser = argparse.ArgumentParser()
    parser.add_argument("result_length", help="Length of obtained results", type=int)
    parser.add_argument("variant", help="Which weekend mode", type=int)

    cli_args = parser.parse_args()

    how_many = cli_args.result_length
    variant = cli_args.variant

    calc = weekend.WeekendCalculator()

    flights = calc.import_from_redis()
    stations = utils.import_stations()
    weekends = calc.weekend_organizer(flights, variant=variant)

    print(f"Variant {variant}")

    print(tabulate.tabulate(table(weekends, stations)[:how_many], tablefmt="psql"))
