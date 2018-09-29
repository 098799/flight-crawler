import json

import ryanair


def import_stations():
    with open("../data/stations.json", "r") as infile:
        return json.load(infile)


def rint(weekend, stations):
    destination = stations[weekend[0].destination]['name']
    date = weekend[0].date
    price = ryanair.combined_price(weekend)
    print(f'{destination} {date}  ---  {price}')


def main():
    stations = import_stations()

    bot = ryanair.RyanairCrawler()

    flights = bot.import_from_redis()

    howmany = 100

    print("-------")
    print("Normal:")
    print("-------")
    weekends = bot.weekend_organizer(flights)

    for weekend in weekends[:howmany]:
        rint(weekend, stations)

    print("-------")
    print("Variant1:")
    print("-------")
    weekends = bot.weekend_organizer(flights, variant=1)

    for weekend in weekends[:howmany]:
        rint(weekend, stations)

    print("-------")
    print("Variant2:")
    print("-------")
    weekends = bot.weekend_organizer(flights, variant=2)

    for weekend in weekends[:howmany]:
        rint(weekend, stations)


if __name__ == '__main__':
    main()
