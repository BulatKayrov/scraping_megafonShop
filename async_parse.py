import asyncio

import aiohttp
from bs4 import BeautifulSoup
import json


async def get_products_all(session, url, _data):
    async with session.get(url=url) as response:
        soup = BeautifulSoup(await response.text(), 'lxml')
        products_list = soup.find_all('div', class_='b-goods-list__item')

        for product in products_list:
            title = product.find('div', class_='b-good__title-entity').text

            product_link = url + (
                product.find('div', class_='b-good__photo photo mobileSmall').find('a').get('href')
            )

            cur_price = product.find('span', class_='b-price-good-list__value b-price__value').text.strip()
            old_price = (
                product.find('span', class_='b-price-good-list__old-price-value b-price__old-price-value').text.strip()
            )
            _data.append({
                'title': title,
                'product_link': product_link,
                'cur_price': cur_price,
                'old_price': old_price,
            })

        print(f'Страница {url} обработана')


async def get_page_count(session, url):
    async with session.get(url=url) as response:
        res = await response.text()
        soup = BeautifulSoup(res, 'lxml')
        pages = soup.find(class_='b-pagination__body').find_all(class_='b-pagination__num')[-1].text
        return int(pages)


async def generate_links(url, session):
    pages = await get_page_count(session=session, url=url)
    return [f'{url}?page={_}' for _ in range(1, pages + 1)]


async def async_main():
    domain_name = 'https://saratov.shop.megafon.ru/mobile'

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(10)) as client:
        links = await generate_links(url=domain_name, session=client)
        tasks = [get_products_all(session=client, url=link, _data=_data) for link in links]
        await asyncio.gather(*tasks)


def main():
    asyncio.run(async_main())

    with open('async.json', 'w') as file:
        json.dump(_data, file)


if __name__ == '__main__':
    _data = []
    main()
