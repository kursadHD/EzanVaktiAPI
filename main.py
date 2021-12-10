from fastapi import FastAPI
from scraper import Scraper
from exceptions import CityNotValid, CountryNotValid

app = FastAPI()
scraper = Scraper()


@app.get('/countryList')
async def country_list():
    try:
        return {
            'ok': True,
            'countryList': list(scraper._country_list.keys())
        }
    except:
        return {
            'ok': False,
            'error': 'INTERNAL_ERROR'
        }


@app.get('/cityList/{country}')
async def city_list(country: str):
    try:
        if country not in scraper._city_ids.keys():
            await scraper._parse_city_ids(country=country)
        return {
            'ok': True,
            'cityList': list(scraper._city_ids[country].keys())
        }
    except:
        return {
            'ok': False,
            'error': 'INTERNAL_ERROR'
        }


@app.get('/daily')
async def daily(country: str, city: str):
    try:
        prayer_times = await scraper.get_daily_prayer_times(country=country, city=city)
        return {
            'ok': True,
            'prayerTimes': prayer_times
        }
    except (CountryNotValid, CityNotValid) as exc:
        return {
            'ok': False,
            'error': str(exc)
        }
    except:
        return {
            'ok': False,
            'error': 'INTERNAL_ERROR'
        }


@app.get('/weekly')
async def daily(country: str, city: str):
    try:
        prayer_times = await scraper.get_weekly_prayer_times(country=country, city=city)
        return {
            'ok': True,
            'prayerTimes': prayer_times
        }
    except (CountryNotValid, CityNotValid) as exc:
        return {
            'ok': False,
            'error': str(exc)
        }
    except:
        return {
            'ok': False,
            'error': 'INTERNAL_ERROR'
        }


@app.get('/monthly')
async def daily(country: str, city: str):
    try:
        prayer_times = await scraper.get_monthly_prayer_times(country=country, city=city)
        return {
            'ok': True,
            'prayerTimes': prayer_times
        }
    except (CountryNotValid, CityNotValid) as exc:
        return {
            'ok': False,
            'error': str(exc)
        }
    except:
        return {
            'ok': False,
            'error': 'INTERNAL_ERROR'
        }