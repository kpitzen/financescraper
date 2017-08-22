'''Main finance scraping control flow module.
   Currently, we only access the Google Finance API,
   and receive output as JSON.'''

from os.path import abspath, join
import argparse
import configparser

import boto3
from multiprocessing import Queue, Process

from financescraper import extractors, loaders, testing, transformers

ARG_PARSER = argparse.ArgumentParser()
SUB_PARSERS = ARG_PARSER.add_subparsers(dest='subparser_name')

NAME_MAPPING_CONFIG_FILE = abspath(join('config', 'name_mappings.conf'))
NAME_MAPPING_CONFIG = configparser.ConfigParser()
NAME_MAPPING_CONFIG.read(NAME_MAPPING_CONFIG_FILE)

FEED_PARSER = SUB_PARSERS.add_parser('feed')
FEED_PARSER.add_argument('-s', '--stock-ticker')
FEED_PARSER.add_argument('-t', '--query-type', choices=['option_chain'], default='option_chain')

ARGS = ARG_PARSER.parse_args()

GOOGLE_FINANCE_URL = 'http://www.google.com/finance'

if __name__ == '__main__':

    MAPPING_QUEUE = Queue()
    LOAD_QUEUE = Queue()

    if ARGS.subparser_name == 'feed':

        EXCEPTION_LOG = abspath('logs/exceptions.log')

        SQS = boto3.resource('sqs')
        TICKER_QUEUE = SQS.get_queue_by_name(QueueName='finance-scraping-queue')

        QUERY_TYPE = ARGS.query_type


        OPTION_MAPPER = transformers.OptionsStockMapper(MAPPING_QUEUE, LOAD_QUEUE
                                                        , NAME_MAPPING_CONFIG)
        MAPPING_PROCESS = Process(target=OPTION_MAPPER.start_listening)

        DATA_LOADER = loaders.BaseFinanceLoader(LOAD_QUEUE, 'finance.options')
        LOAD_PROCESS = Process(target=DATA_LOADER.start_listening)

        LOAD_PROCESS.start()
        MAPPING_PROCESS.start()
        while True:
            with open(EXCEPTION_LOG, 'w') as exception_log:
                STOCK_TICKER_LIST = TICKER_QUEUE.receive_messages()
                if STOCK_TICKER_LIST:
                    for message in STOCK_TICKER_LIST:
                        try:
                            ticker = message.body
                            message.delete()
                            print(ticker)
                            QUERY_PAYLOAD = '?q={}&output=json'.format(ticker)
                            URL_PAYLOAD = '/'.join([GOOGLE_FINANCE_URL, ''.join([QUERY_TYPE, QUERY_PAYLOAD])])
                            print(URL_PAYLOAD)
                            TEST_DATA_GETTER = extractors.BaseStockDataPump(URL_PAYLOAD, ticker
                                                                            , output_queue=MAPPING_QUEUE)

                            DATA_FEED_PROCESS = Process(target=TEST_DATA_GETTER.feed_data)
                            DATA_FEED_PROCESS.start()
                            DATA_FEED_PROCESS.join()
                            print('Finished loading: {}'.format(ticker))
                        except Exception as exception:
                            print(exception, file=exception_log)
                            continue
        MAPPING_PROCESS.join()
        LOAD_PROCESS.join()
