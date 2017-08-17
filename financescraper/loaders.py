'''Given a list of records, inserts those records into the options table'''

import boto3

class BaseFinanceLoader():
    '''Base class to be extended if needed'''

    def __init__(self, input_queue, table_name):
        self._input_queue = input_queue
        self.table_name = table_name

    def start_listening(self):
        print('>>Listening for loading data...')
        dynamodb = boto3.resource('dynamodb')
        while True:
            message = self._input_queue.get()
            if message != 'kill':
                table = dynamodb.Table(self.table_name)
                for item in message:
                    table.put_item(Item=item)

                # with table.batch_writer() as batch:
                #     for item in message:
                #         print(item)
                #         batch.put_item(item)
            else:
                break
