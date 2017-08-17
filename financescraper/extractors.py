'''Contains classes and methods dedicated to scraping web finance data'''

from json.decoder import JSONDecodeError

import demjson
import requests


class BaseStockDataPump():
    '''Base class for intake of stock data'''

    def __init__(self, url, stock_name, output_queue = None, chunk_size: int = 5):
        self._url = url
        self._data = None
        self._get_stock_data()
        self._stock_name = stock_name
        self._output_queue = output_queue
        self._chunk_size = chunk_size

    def _get_stock_data(self):
        data_request = requests.get(self._url)
        try:
            assert 'application/json' in data_request.headers['Content-Type']
        except AssertionError:
            raise NotImplementedError('We require JSON returns!')
        try:
            request_data = data_request.json()
        except JSONDecodeError:
            request_data = data_request.text
            request_data = demjson.decode(request_data)
        self._data = request_data

    def feed_data(self):
        print('>>Feeding {} data...'.format(self._stock_name))
        self._output_queue.put((self._stock_name, self._data))
        self._output_queue.put('kill')
