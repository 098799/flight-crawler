from flight_crawler import session

import pytest

from requests import exceptions


@pytest.fixture
def trial_session():
    return session.Session()


def test_proxy_list(trial_session):
    proxy_list = trial_session.proxy_list
    assert len(proxy_list) > 500


def test_free_proxy_read(trial_session):
    proxy = trial_session.free_proxy
    assert "https" in proxy
    assert ":" in proxy['https']
    assert len(proxy['https'].split(".")) == 4


def test_get(trial_session, mocker):
    m_get = mocker.patch('requests.Session.get')

    trial_session.get("ryanair.com")

    assert m_get.call_count == 1
    assert 'ryanair.com' in m_get.call_args[0]
    assert 'timeout' in m_get.call_args[1]
    assert 'proxies' in m_get.call_args[1]


def test_get__bad_response(trial_session, mocker):
    m_get = mocker.patch(
        'requests.Session.get',
        side_effect=exceptions.ProxyError
    )

    response = trial_session.get("ryanair.com")

    assert not response
    assert m_get.call_count == 10
