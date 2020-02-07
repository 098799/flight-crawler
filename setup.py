from setuptools import setup


setup(
    name="flight_crawler", entry_points={"console_scripts": ["crawl=main:crawl", "weekend=main:calculate_weekend"]},
)
