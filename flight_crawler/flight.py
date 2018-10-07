import datetime


class Flight(object):
    def __init__(self, key, value):
        key = key.decode()

        self.date = datetime.datetime.fromisoformat(key[:10] + "T" + key[-5:] + ":00")
        self.origin = key[10:13]
        self.destination = key[13:16]
        self.price = float(value.decode())
