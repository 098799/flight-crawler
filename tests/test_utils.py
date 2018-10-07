from flight_crawler import flight
from flight_crawler import utils

import pytest


@pytest.fixture
def weekend():
    return [
        flight.Flight(
            b"2018-01-01BCNSXF20:00", b'20.00'
        ),
        flight.Flight(
            b"2018-01-03SXFBCN20:00", b'20.00'
        )
    ]


def test_sys_argv():
    sys_argv = utils.return_sys_argv()

    assert sys_argv[0].split("/")[-1] == "pytest"


def test_combined_price(weekend):
    assert utils.combined_price(weekend) == [40.0]
