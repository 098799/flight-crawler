from flight_crawler import crawler

import pytest


@pytest.fixture
def bot():
    return crawler.Crawler()


# def test_request(bot):
    # bot.crawl()
