import logging
import os
import sys
import time

sys.path.append('./src')
import oom_messages_exporter

log = os.getenv('example_tailer_file')

if __name__ == '__main__':
    logging.basicConfig(format = '%(asctime)s %(message)s', level=20)

def process_a_line(line):
    logging.warning('There is a line: "{}".'.format(line))

tailer = oom_messages_exporter.FileTailer(file=log)

def main():
    while True:
        data = tailer.tail()
        for line in data:
            process_a_line(line)
        time.sleep(0.01)

if __name__ == '__main__':
    main()
