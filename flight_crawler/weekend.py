import json

from flight_crawler import crawler
from flight_crawler import utils

import tabulate


def import_stations():
    stations = utils.read_from_file("data/stations.json")
    return json.loads(stations)


def table(weekends, stations):
    table = []

    for weekend in weekends:
        destination = stations[weekend[0].destination]['name']
        date = weekend[0].date
        price = utils.combined_price(weekend)
        table.append([destination, date, price])

    return table


def main():
    argv = utils.return_sys_argv()
    howmany = int(argv[1])
    variant = int(argv[2])

    bot = crawler.Crawler()

    flights = bot.import_from_redis()
    stations = import_stations()
    weekends = bot.weekend_organizer(flights, variant=variant)

    print(f"Variant {variant}")

    print(
        tabulate.tabulate(
            table(weekends, stations)[:howmany],
            tablefmt="psql"
        )
    )


if __name__ == '__main__':
    main()
