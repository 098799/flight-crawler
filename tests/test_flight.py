import datetime

from flight_crawler import flight

import pytest


@pytest.fixture
def flight_instance():
    return flight.Flight(
        b"2018-01-01BCNSXF20:00", b'20.00'
    )


def test_attributes(flight_instance):
    assert flight_instance.price == 20.00
    assert flight_instance.date == datetime.datetime(2018, 1, 1, 20, 0)
    assert flight_instance.origin == "BCN"
    assert flight_instance.destination == "SXF"
