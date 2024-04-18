import json
import logging
import os
import requests

from kafka import KafkaProducer

logging.basicConfig(format='%(asctime)s %(module)s [%(levelname)s]: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

STEP = 1000
API_URL = 'https://api.litres.ru/foundation/api/arts/facets'
LIMIT = 2*10**3
try:
    LIMIT = int(os.environ['LITRES_BOOKS_COUNT_LIMIT'])
except ValueError as _:
    logger.warning("Could not parse value of environtment variable 'LITRES_BOOKS_COUNT_LIMIT'. "
                   "Falling back to default value: %d", LIMIT)
except KeyError as _:
    logger.warning("Could not find environtment variable 'LITRES_BOOKS_COUNT_LIMIT'. "
                   "Falling back to default value: %d", LIMIT)

producer = KafkaProducer(bootstrap_servers=['kafka:9092'],
                         value_serializer=lambda x: json.dumps(x, ensure_ascii=False).encode('utf-8'))

def send_to_kafka(topic, data):
    producer.send(topic, value=data)
    producer.flush()

def books_overview_gen(total_limit: int = LIMIT):
    logger.debug('Started books list extraction')
    total_books = 0
    skipped_offset_values = 0
    params = {
        'offset': total_books,
        'limit': STEP,
        'o': 'new'
    }
    while total_books < total_limit:
        logger.info('Requesting books from %d to %d',
                    params['offset'], params['offset'] + params['limit'])
        res = requests.get(API_URL, params=params)
        if res.status_code == 200:
            books_data = res.json()['payload']['data']
            for book_data in books_data:
                logger.debug('Received info for book %s (id: %d, url: %s)',
                             book_data['title'],
                             book_data['id'],
                             book_data['url'])
                total_books += 1
                logger.debug('Total books received: %d', total_books)
                yield book_data
                if total_books > total_limit:
                    return
        elif res.status_code >= 500:
            skipped_offset_values += 100
            logger.warning('Server error occured, when receiving books from %d to %d',
                           params['offset'], params['offset'] + params['limit'])
        else:
            logger.error('Books retrieval failed with status code %d', res.status_code)
        params['offset'] = total_books + skipped_offset_values


if __name__ == "__main__":
    for book in books_overview_gen(LIMIT):
        send_to_kafka('books_overviews', book)
