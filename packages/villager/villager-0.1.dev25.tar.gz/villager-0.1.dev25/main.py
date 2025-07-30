# -*- coding: utf-8 -*-
from init import init
from interfaces.boot import main
from tools.logging import logging, LoggingToFile

if __name__ == '__main__':
    logging.set_logging_stream(LoggingToFile(filename="log.json"))
    init()
    main()
