import aiohttp
from typing import Dict, Any, Callable
from unidecode import unidecode
from .country_list import COUNTRY_LIST
from .exceptions import CountryNotValid, CityNotValid


def uppercase_and_unidecode_params(func: Callable) -> Callable:
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        for key, value in kwargs.items():
            try:
                kwargs[key] = unidecode(value).upper()
            except:
                pass
        return await func(*args, **kwargs)
    return wrapper


class Scraper:
    def __init__(self) -> None:
        self._prayer_time_url_format: str = 'https://namazvakitleri.diyanet.gov.tr/en-US/{}/ilce-icin-namaz-vakti'
        self._state_ids_json_url_format: str = 'https://namazvakitleri.diyanet.gov.tr/assets/locations/{}.json'
        self._country_list: Dict[str, str] = {
            country['CountryName']: str(country['CountryID']) for country in COUNTRY_LIST
        }
        self._city_ids: Dict[str, Any] = {}

    @uppercase_and_unidecode_params
    async def _get_id(self, *, country: str, city: str) -> str:
        if country not in self._country_list.keys():
            raise CountryNotValid(f'{country} is not valid.')
        if country not in self._city_ids.keys():
            await self._parse_city_ids(country=country)

        if city not in self._city_ids[country].keys():
            raise CityNotValid(f'{city} is not valid.')
        return self._city_ids[country][city]

    @uppercase_and_unidecode_params
    async def _parse_city_ids(self, *, country: str) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(self._state_ids_json_url_format.format(country)) as response:
                city_ids = {}
                cities = await response.json()
                if country == 'TURKEY':
                    for city in cities:
                        if city['State'] == city['City']:
                            city_ids[city['State']] = city['CityID']
                else:
                    for city in cities:
                        city_ids[city['City']] = city['CityID']
        self._city_ids.update({country: city_ids})

    @uppercase_and_unidecode_params
    async def get_daily_prayer_times(self, *, country: str, city: str) -> Dict[str, str]:
        async with aiohttp.ClientSession() as session:
            city_id = await self._get_id(country=country, city=city)
            async with session.get(self._prayer_time_url_format.format(city_id)) as response:
                text = await response.text()
                text = text.split(
                    '<div class="w3-row" id="today-pray-times-row">')[1]
                rows = [row.split('</div>')[0]
                        for row in text.split('<div class="tpt-time">')[1:]]
                return {
                    'imsak': rows[0],
                    'gunes': rows[1],
                    'ogle': rows[2],
                    'ikindi': rows[3],
                    'aksam': rows[4],
                    'yatsi': rows[5]
                }

    @uppercase_and_unidecode_params
    async def get_weekly_prayer_times(self, *, country: str, city: str) -> Dict[str, Dict[str, str]]:
        weekly = {}
        async with aiohttp.ClientSession() as session:
            city_id = await self._get_id(country=country, city=city)
            async with session.get(self._prayer_time_url_format.format(city_id)) as response:
                text = await response.text()
                text = text.split(
                    '<div id = "tab-0" class="w3-container w3-border nv-tab-content">'
                )[1].split('<tbody>')[1].split('</tbody>')[0]
                days = [day.split('</tr>')[0]
                        for day in text.split('<tr>')][1:]
                for day in days:
                    rows = [row.split('</td>')[0] for row in day.split('<td>')]
                    prayer_times = {
                        'imsak': rows[2],
                        'gunes': rows[3],
                        'ogle': rows[4],
                        'ikindi': rows[5],
                        'aksam': rows[6],
                        'yatsi': rows[7]
                    }
                    weekly.update({rows[1]: prayer_times})
        return weekly

    @uppercase_and_unidecode_params
    async def get_monthly_prayer_times(self, *, country: str, city: str) -> Dict[str, Dict[str, str]]:
        monthly = {}
        async with aiohttp.ClientSession() as session:
            city_id = await self._get_id(country=country, city=city)
            async with session.get(self._prayer_time_url_format.format(city_id)) as response:
                text = await response.text()
                text = text.split(
                    '<div id = "tab-1" class="w3-container w3-border nv-tab-content" style="display:none">'
                )[1].split('<tbody>')[1].split('</tbody>')[0]
                days = [day.split('</tr>')[0]
                        for day in text.split('<tr>')][1:]
                for day in days:
                    rows = [row.split('</td>')[0] for row in day.split('<td>')]
                    prayer_times = {
                        'imsak': rows[2],
                        'gunes': rows[3],
                        'ogle': rows[4],
                        'ikindi': rows[5],
                        'aksam': rows[6],
                        'yatsi': rows[7]
                    }
                    monthly.update({rows[1]: prayer_times})
        return monthly

