import asyncio

from aiohttp import ClientSession
from xml.etree import ElementTree


class HTTPClient:
    CENTRAL_BUNK_API = 'https://cbr.ru/scripts/XML_daily.asp'

    def __init__(self, uri: str = CENTRAL_BUNK_API):
        self.session = ClientSession()
        self.uri = uri
        self.current_data = None

    async def get(self):
        async with self.session.get(self.CENTRAL_BUNK_API) as response:
            self.current_data = await response.text()

    async def close(self):
        await self.session.close()

    async def get_data_xml(self) -> ElementTree:
        try:
            return ElementTree.fromstring(self.current_data)
        except TypeError:
            return 'Данные не были заполнены, проверьте вызов метода get()'


if __name__ == '__main__':
    async def main():
        client = HTTPClient()
        try:
            print(await client.get())
            print(client.current_data)
            print(await client.get_data_xml())
        finally:
            await client.close()


    asyncio.run(main())
