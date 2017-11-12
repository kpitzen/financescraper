'''Main finance scraping control flow module.
   Currently, we only access the Google Finance API,
   and receive output as JSON.'''

from os.path import abspath, join
import argparse
import configparser
import atexit

from multiprocessing import Queue, Process

from financescraper import extractors, loaders, testing, transformers

from flask import Flask, request, abort

NAME_MAPPING_CONFIG_FILE = abspath(join('config', 'name_mappings.conf'))
NAME_MAPPING_CONFIG = configparser.ConfigParser()
NAME_MAPPING_CONFIG.read(NAME_MAPPING_CONFIG_FILE)


GOOGLE_FINANCE_URL = 'http://www.google.com/finance'


APP = Flask(__name__)

MAPPING_QUEUE = Queue()
LOAD_QUEUE = Queue()


EXCEPTION_LOG = abspath('logs/exceptions.log')


OPTION_MAPPER = transformers.OptionsStockMapper(MAPPING_QUEUE, LOAD_QUEUE
                                                , NAME_MAPPING_CONFIG)
MAPPING_PROCESS = Process(target=OPTION_MAPPER.start_listening)

DATA_LOADER = loaders.BaseFinanceLoader(LOAD_QUEUE, 'finance.options')
LOAD_PROCESS = Process(target=DATA_LOADER.start_listening)

LOAD_PROCESS.start()
MAPPING_PROCESS.start()
atexit.register(MAPPING_PROCESS.join)
atexit.register(LOAD_PROCESS.join)
@APP.route('/option_chain')
def feed_ticker_data():
    ticker = request.args.get('ticker')
    with open(EXCEPTION_LOG, 'w') as exception_log:
        try:
            print(ticker)
            QUERY_PAYLOAD = '?q={}&output=json'.format(ticker)
            URL_PAYLOAD = '/'.join([GOOGLE_FINANCE_URL, ''.join(['option_chain', QUERY_PAYLOAD])])
            print(URL_PAYLOAD)
            TEST_DATA_GETTER = extractors.BaseStockDataPump(URL_PAYLOAD, ticker
                                                            , output_queue=MAPPING_QUEUE)
            DATA_FEED_PROCESS = Process(target=TEST_DATA_GETTER.feed_data)
            DATA_FEED_PROCESS.start()
            DATA_FEED_PROCESS.join()
            return 'STATUS:Finished loading: {}'.format(ticker)
        except Exception as exception:
            print(exception, file=exception_log)
            abort(404)

if __name__ == '__main__':
    APP.run(host='0.0.0.0')