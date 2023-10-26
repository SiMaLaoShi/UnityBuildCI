import io
import os
import sys
import time
from threading import Thread

from PyQt5.QtCore import pyqtSignal, QObject


class Logger(QObject):
    log_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._original_stdout = None

    def start(self):
        self._original_stdout = sys.stdout
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='gb18030')

    def stop(self):
        sys.stdout = self._original_stdout

    def emit_log(self, log_line):
        self.log_received.emit(log_line.rstrip())
        if sys.stdout is not None:
            sys.stdout.flush()


class Tail(QObject, Thread):
    def __init__(self, filename):
        QObject.__init__(self)
        Thread.__init__(self)
        self._filename = filename
        self._stop_reading = False
        self._logger = Logger()

    def run(self):
        while not self._stop_reading and not os.path.exists(self._filename):
            time.sleep(0.1)
        with self.open_default_encoding(self._filename, mode='r') as file:
            while True:
                where = file.tell()
                line = file.readline()
                if self._stop_reading and not line:
                    break
                if not line:
                    time.sleep(1)
                    file.seek(where)
                else:
                    self._logger.emit_log(line)

    def stop(self):
        self._stop_reading = True
        # Wait for thread to read the remaining log after process quit for 5 seconds
        self.join()
        self._logger.stop()
        print('Thread killed!')

    @staticmethod
    def open_default_encoding(file, mode):
        return open(file, mode=mode, encoding='utf-8-sig')

    @property
    def logger(self):
        return self._logger

