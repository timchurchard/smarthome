
import sys

import logging

logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)s [%(name)s] {%(threadName)s} %(message)s',
                            level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


from . import webserver


def main():
    webserver.main()


if __name__ == '__main__':
    sys.exit(main())
