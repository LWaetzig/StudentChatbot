import time


class FileProcessor():
    def __init__(self, file) -> None:
        self.file = file
        pass


    def process(self):
        time.sleep(2)
        return True