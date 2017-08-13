'''Main finance scraping control flow module.
   Currently, we only access the Google Finance API,
   and receive output as JSON.'''

import argparse
from multiprocessing import Queue, Process

from financescraper import extractors, loaders, testing, transformers

ARG_PARSER = argparse.ArgumentParser()
SUB_PARSERS = ARG_PARSER.add_subparsers(dest='subparser_name')

FEED_PARSER = SUB_PARSERS.add_parser('feed')
FEED_PARSER.add_argument('-s', '--stock-ticker')
FEED_PARSER.add_argument('-t', '--query-type', choices=['option_chain'], default='option_chain')

ARGS = ARG_PARSER.parse_args()

GOOGLE_FINANCE_URL = 'http://www.google.com/finance'

if __name__ == '__main__':

    TEST_OUTPUT_QUEUE = Queue()



    if ARGS.subparser_name == 'feed':
        TICKER_NAME = ARGS.stock_ticker
        QUERY_TYPE = ARGS.query_type
        QUERY_PAYLOAD = '?q={}&output=json'.format(TICKER_NAME)
        URL_PAYLOAD = '/'.join([GOOGLE_FINANCE_URL, ''.join([QUERY_TYPE, QUERY_PAYLOAD])])

