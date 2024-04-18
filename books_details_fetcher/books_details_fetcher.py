import aiohttp
import asyncio
import logging
import json

from aiokafka import AIOKafkaConsumer
from elasticsearch import AsyncElasticsearch

logging.basicConfig(format='%(asctime)s %(module)s [%(levelname)s]: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DEFAULT_API_ENDPOINT = 'https://api.litres.ru/foundation/api/arts'

async def consume():
    print('Before async with')
    async with aiohttp.ClientSession() as session:
        async with AsyncElasticsearch(hosts=["http://elasticsearch:9200"]) as es_client:
            print('After async with')
            consumer = AIOKafkaConsumer(
                'books_overviews',
                bootstrap_servers='kafka:9092',
                value_deserializer=lambda x: json.loads(x.decode('utf-8')))
            await consumer.start()
            try:
                async for msg in consumer:
                    book_overview = msg.value
                    # Now, process each book overview as before
                    logger.info(f"Processing book: {book_overview['title']}")
                    if book_overview is None:
                        return
                    book_data = await process_book(book_overview, session)
                    logger.info(f"Processed book: {book_data['title']}, Now putting it to DB")
                    await es_client.index(index="books", document=book_data)
                    logger.info(f"Book: {book_data['title']} must now be in DB")
            finally:
                await consumer.stop()


async def fetch(url, session: aiohttp.ClientSession):
    logger.debug('Fetching info for book at %s', url)
    async with session.get(DEFAULT_API_ENDPOINT + url) as response:
        res = await response.json()
        logger.debug('Done fetching info for book at %s', url)
        return res

async def process_book(boook_overview, session: aiohttp.ClientSession):
    logger.debug('Fetching info for book %s', boook_overview['title'])
    book_detailed_info = await fetch(boook_overview['url'], session)
    book_clean_info = book_detailed_info['payload']['data']
    # TODO: implement data cleaning and processing
    # book_clean_info = clean_book_data(book_detailed_info)
    return book_clean_info

if __name__ == "__main__":
    asyncio.run(consume())
