import sys


def combined_price(weekend):
    return [round(weekend[0].price + return_flight.price, 2)
            for return_flight in weekend[1:]]


def read_from_file(file_name):
    with open(file_name, "r") as infile:
        return infile.read()


def return_sys_argv():
    return sys.argv
