import json

import requests
from bs4 import BeautifulSoup
from fake_useragent import FakeUserAgent


def get_page_count(session, url):
    response = session.get(url=url, headers=headers).text
    soup = BeautifulSoup(response, 'lxml')
    pages = soup.find(class_='b-pagination__body').find_all(class_='b-pagination__num')[-1].text
    return int(pages)


def generate_links(url, session):
    pages = get_page_count(session=session, url=url)
    return [f'{url}?page={_}' for _ in range(1, pages + 1)]


def get_products_all(session, url):
    _data = []

    links = generate_links(url=url, session=session)

    for page, link in enumerate(links, 1):
        response = session.get(url=link, headers=headers).text
        soup = BeautifulSoup(response, 'lxml')
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

        print(f'Страница {page} обработана')

    return _data


def main():
    domain_name = 'https://saratov.shop.megafon.ru/mobile'

    with requests.session() as session:
        res = get_products_all(session=session, url=domain_name)

    with open('sync.json', 'w') as file:
        json.dump(res, file)


if __name__ == '__main__':
    headers = {'User-Agent': FakeUserAgent().chrome}
    main()

