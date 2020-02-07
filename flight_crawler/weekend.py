import datetime

from flight_crawler import flight
from flight_crawler import redis_entity
from flight_crawler import utils


class WeekendCalculator(redis_entity.RedisEntity):
    def import_from_redis(self):
        keys = self.redis.keys()
        weekend_keys = filter(lambda key: key.decode()[0] != "w", keys)
        flights = []

        for key in weekend_keys:
            flights.append(flight.Flight(key, self.redis.get(key)))

        return flights

    def match(self, begin, end):
        conditions = [
            datetime.timedelta(0) < (end.date - begin.date) <= datetime.timedelta(5),
            begin.destination == end.origin,
        ]
        return True if all(conditions) else False

    def weekend_begin_condition(self, flight_list, variant):
        conditions = [flight_list.origin == "BCN"]
        if variant == 0:
            conditions.extend(
                [flight_list.date.strftime("%a") == "Fri", int(flight_list.date.strftime("%H")) >= self.CUTOFF_FRIDAY]
            )
        elif variant == 1:
            conditions.extend(
                [flight_list.date.strftime("%a") == "Thu", int(flight_list.date.strftime("%H")) >= self.CUTOFF_THURSDAY]
            )
        elif variant == 2:
            conditions.extend(
                [flight_list.date.strftime("%a") == "Fri", int(flight_list.date.strftime("%H")) >= self.CUTOFF_FRIDAY]
            )
        return all(conditions)

    def weekend_end_condition(self, flight_list, variant):
        conditions = [int(flight_list.date.strftime("%H")) >= self.CUTOFF_RETURN, flight_list.origin != "BCN"]
        if variant == 0:
            conditions.append(flight_list.date.strftime("%a") == "Sun")
        elif variant == 1:
            conditions.append(flight_list.date.strftime("%a") == "Sun")
        elif variant == 2:
            conditions.append(flight_list.date.strftime("%a") == "Mon")
        return all(conditions)

    def weekend_organizer(self, flights, variant=0):
        weekend_beginnings = filter(lambda flight_list: self.weekend_begin_condition(flight_list, variant), flights,)
        weekend_ends = list(filter(lambda flight_list: self.weekend_end_condition(flight_list, variant), flights,))
        weekends = []

        for flight_ in weekend_beginnings:
            weekends.append([flight_])

            for return_flight in weekend_ends:
                if self.match(flight_, return_flight):
                    weekends[-1].append(return_flight)

        sorted_weekends = sorted(filter(lambda weekend: len(weekend) > 1, weekends), key=utils.combined_price)

        destinations = {flight[0].destination for flight in sorted_weekends}

        return_list = []

        for destination in destinations:
            for weekend in sorted_weekends:
                if (
                    weekend[0].destination == destination
                    and len(list(filter(lambda w: w[0].destination == destination, return_list)))
                    < self.HOW_MANY_FLIGHTS_TO_SHOW
                ):
                    return_list.append(weekend)

        return sorted(return_list, key=utils.combined_price)
