import pytest

from .. import ryanair


@pytest.fixture
def bot():
    return ryanair.RyanairCrawler()


def test_request(bot):
    bot.crawl()
