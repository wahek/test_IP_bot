import asyncio
import json

from aiohttp import ClientSession
from xml.etree import ElementTree


class HTTPClient:
    CENTRAL_BUNK_API = 'https://cbr.ru/scripts/XML_daily.asp'

    def __init__(self, uri: str = CENTRAL_BUNK_API):
        self.__session = ClientSession()
        self.__uri = uri
        self.__current_data = None
        self.data: list[dict] | None = None
        self.keys: dict | None = None

    async def __get(self):
        async with self.__session.get(self.CENTRAL_BUNK_API) as response:
            self.__current_data = await response.text()

    async def close(self):
        await self.__session.close()

    async def __get_data_xml(self) -> ElementTree:
        try:
            return ElementTree.fromstring(self.__current_data)
        except TypeError:
            return 'Данные не были заполнены, проверьте вызов метода get()'

    async def __parse_elements(self):
        currencies = []
        data = await self.__get_data_xml()
        for valute in data.findall('Valute'):
            char_code = valute.find('CharCode').text
            name = valute.find('Name').text
            value = valute.find('Value').text
            currencies.append({
                char_code:
                    {
                        'CharCode': char_code,
                        'Name': name,
                        'Value': value
                    }
            })
        return currencies

    async def __fill_data(self):
        await self.__get()
        await self.__get_data_xml()
        self.data = await self.__parse_elements()

    async def __fill_keys(self, key='valute'):
        current_keys = set()
        for item in self.data:
            for k in item.keys():
                current_keys.add(k)
        self.keys = {key: current_keys}

    async def update(self):
        await self.__fill_data()
        await self.__fill_keys()

    async def get_data(self):
        await self.update()
        return self.data


if __name__ == '__main__':
    async def main():
        client = HTTPClient()
        try:
            print(await client.get_data())
            print(client.keys)
        finally:
            await client.close()


    asyncio.run(main())
