CURRENCY_URL = "http://free.currencyconverterapi.com/api/v5/convert?q=EUR_{}&compact=y"
JSON_URL = "https://desktopapps.ryanair.com/v4/en-ie/availability"

HEADERS = {
    "origin": "https://www.ryanair.com",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "user-agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) " "Chrome/68.0.3440.106 Safari/537.36"
    ),
    "accept": "application/json, text/plain, */*",
    "authority": "desktopapps.ryanair.com",
    "cache-control": "no-cache",
}

PARAMS = {
    "ADT": "1",
    "CHD": "0",
    "FlexDaysIn": "6",
    "FlexDaysOut": "6",
    "INF": "0",
    "IncludeConnectingFlights": "true",
    "RoundTrip": "true",
    "TEEN": "0",
    "ToUs": "AGREED",
    "exists": "false",
}
