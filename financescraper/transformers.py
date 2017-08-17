'''handles renaming of keys and formatting of data for loads'''

from helpers import helpers
import abc
import json

class BaseStockMapper():
    '''takes data fed from an extractor, applies appropriate logic,
       and feeds data to a loader'''

    __metaclass__ = abc.ABCMeta

    def __init__(self, input_queue, output_queue, config=None, pull_type=None):
        self._input_queue = input_queue
        self._output_queue = output_queue
        if config:
            self._name_mappings = helpers.parse_config_section_to_dict(config, pull_type)
        else:
            self._name_mappings = None

    def start_listening(self):
        '''listens to the input queue, applies mapping logic,
           and sends messages to the output queue'''
        print('>>Listening for mapping data...')
        while True:
            message = self._input_queue.get()
            if message != 'kill':
                output_message = self.mapping_logic(message)
                self._output_queue.put(output_message)
            else:
                self._output_queue.put('kill')
                break

    @abc.abstractmethod
    def mapping_logic(self, message):
        '''given a raw data message, returns mapped version of that message'''
        raise NotImplementedError('Need to override in subclasses!')


class OptionsStockMapper(BaseStockMapper):
    '''feeds data for option chains'''

    def __init__(self, input_queue, output_queue, config=None):
        BaseStockMapper.__init__(self, input_queue, output_queue, config, pull_type='options')
        print(self._name_mappings)

    def mapping_logic(self, message):
        results = []
        ticker = message[0]
        puts_data = message[1]['puts']
        calls_data = message[1]['calls']
        for item in puts_data:
            output_item = {}
            for key, value in item.items():
                if value:
                    mapped_key = self._name_mappings.get(key, key)
                    output_item[mapped_key] = value
            output_item['option_type'] = 'put'
            output_item['stock_ticker'] = ticker
            output_item['contract_id'] = int(output_item['contract_id'])
            # results.append(helpers.format_python_dict_for_dynamo(output_item))
            results.append(output_item)
        for item in calls_data:
            output_item = {}
            for key, value in item.items():
                if value:
                    mapped_key = self._name_mappings.get(key, key)
                    output_item[mapped_key] = value
            output_item['option_type'] = 'call'
            output_item['stock_ticker'] = ticker
            output_item['contract_id'] = int(output_item['contract_id'])
            # results.append(helpers.format_python_dict_for_dynamo(output_item))
            results.append(output_item)
        return results
