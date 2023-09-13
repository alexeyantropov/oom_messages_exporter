from oom_messages_exporter.exporter import main

import logging

if __name__ == '__main__':
    logging.basicConfig(format = '%(asctime)s %(message)s', level=20)
    main()