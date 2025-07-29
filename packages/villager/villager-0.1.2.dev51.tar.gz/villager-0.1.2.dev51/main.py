from interfaces.boot import main
from tools.logging import logging,LoggingToFile

if __name__ == '__main__':
    logging.set_logging_stream(LoggingToFile(filename="log.json"))
    main()