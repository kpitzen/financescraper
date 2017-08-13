'''Container for all testing classes and methods internal to the process
   (Not Unit Testing)'''

class TestListener():

    def __init__(self, input_queue):
        self._queue = input_queue

    def start_listener(self):
        while True:
            message = self._queue.get()
            try:
                assert message != 'kill'
            except AssertionError:
                self._queue.put('kill')
                break
            else:
                print(message)
