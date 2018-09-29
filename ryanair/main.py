import logging
import re
import sys

import ryanair


def input_read():
    arguments = sys.argv[1:]
    airports = []
    days = []

    for argument in arguments:
        if re.match(r'\d', argument):
            days.append(argument)
        else:
            airports.append(argument)

    return airports, days


def main():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    airports, days = input_read()

    bot = ryanair.RyanairCrawler()

    bot.crawl(
        days,
        destination=airports[0],
        origin=airports[1]
    )


if __name__ == '__main__':
    main()
