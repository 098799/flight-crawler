import json


def combined_price(weekend):
    return [round(weekend[0].price + return_flight.price, 2) for return_flight in weekend[1:]]


def import_stations():
    with open("data/stations.json", "r") as infile:
        return json.load(infile)
