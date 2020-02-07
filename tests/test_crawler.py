import datetime

from flight_crawler import crawler

import responses

from . import testutils


@responses.activate
def test_request():
    """Full bot test with mocked response."""
    responses.add(
        responses.GET,
        "https://desktopapps.ryanair.com/v4/en-ie/availability",
        json=testutils.open_json_fixture("response.json"),
    )

    results = crawler.Crawler().crawl(
        datetime.datetime.fromisoformat("2020-02-15"), datetime.datetime.fromisoformat("2020-02-16"), "BCN", "SXF"
    )

    assert results == {
        "2020-02-15BCNSXF06:35": 81.99,
        "2020-02-15BCNSXF16:25": 39.3,
        "2020-02-15SXFBCN09:45": 128.99,
        "2020-02-15SXFBCN13:15": 72.24,
        "2020-02-16BCNSXF06:35": 81.99,
        "2020-02-16BCNSXF16:25": 194.99,
        "2020-02-16SXFBCN09:45": 128.99,
        "2020-02-16SXFBCN13:15": 291.99,
        "2020-02-17BCNSXF06:35": 194.99,
        "2020-02-17BCNSXF16:25": 167.99,
        "2020-02-17SXFBCN09:45": 81.99,
        "2020-02-17SXFBCN13:15": 81.99,
        "2020-02-18BCNSXF16:25": 291.99,
        "2020-02-18SXFBCN13:15": 99.99,
        "2020-02-19BCNSXF16:25": 194.99,
        "2020-02-19SXFBCN13:15": 99.99,
        "2020-02-20BCNSXF16:25": 117.99,
        "2020-02-20SXFBCN13:15": 69.99,
        "2020-02-21BCNSXF06:35": 230.99,
        "2020-02-21BCNSXF16:25": 291.99,
        "2020-02-21SXFBCN09:45": 69.99,
        "2020-02-21SXFBCN13:15": 81.99,
    }
