from flight_crawler import main


def test_parse_arguments(mocker):
    mocker.patch(
        'flight_crawler.utils.return_sys_argv',
        return_value=['main.py', 'BCN', 'SXF', "2018-01-01", "2018-01-03"]
    )

    arguments = main.parse_arguments()

    assert arguments[0] == ['BCN', 'SXF']
    assert arguments[1] == ['2018-01-01', '2018-01-03']


def test_main(mocker):
    bot = mocker.patch('flight_crawler.crawler.Crawler')
    mocker.patch(
        'flight_crawler.main.parse_arguments',
        return_value=[["foo", "bar"], []],
    )

    main.main()

    assert bot.call_count == 1
