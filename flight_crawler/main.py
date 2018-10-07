import logging
import re

from flight_crawler import crawler
from flight_crawler import utils


def main():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    airports, days = parse_arguments()

    bot = crawler.Crawler()

    bot.crawl(
        days,
        destination=airports[0],
        origin=airports[1],
    )


def parse_arguments():
    arguments = utils.return_sys_argv()[1:]
    airports = []
    days = []

    for argument in arguments:
        if re.match(r'\d', argument):
            days.append(argument)
        else:
            airports.append(argument)

    return airports, days


if __name__ == '__main__':
    main()
