import re
import sys

import ryanair


def print_line():
    print("+" + "-" * 90 + "+")


def pretty_print(something):
    print("| " + something + " " * (88-len(something)) + " |")


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
    airports, days = input_read()

    bot = ryanair.RyanairCrawler()

    if len(airports) == 1:
        flight, output = bot.crawl(days, destination=airports[0])
    else:
        flight, output = bot.crawl(days, destination=airports[0], origin=airports[1])

    print_line()
    pretty_print(flight)
    print_line()

    for date, results in output.items():
        pretty_print(date)
        pretty_print("")

        for result in results:
            departure = result['departure']
            arrival = result['arrival']
            duration = result['duration']
            price = result['price']

            fstring = f"{departure}-{arrival} ({duration}), {price}"
            pretty_print(fstring)

        print_line()


if __name__ == '__main__':
    main()
