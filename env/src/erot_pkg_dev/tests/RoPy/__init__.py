import os
import sys
import logging
import argparse
import traceback


class LevelFilter(logging.Filter):
    def __init__(self, *args, **kwargs):
        super(LevelFilter, self).__init__()
        # self.__level = []
        # for i in args:
        #     self.__level.append(i)
        self.__level = args[0]

    def filter(self, record):
        # return record.levelno in self.__level
        return record.levelno >= self.__level


class CustFormatter(logging.Formatter):
    def format(self, record):
        if record.pathname:
            record.pathname = os.path.abspath(record.pathname)
        return super(CustFormatter, self).format(record)


def addLoggingLevel(levelName, levelNum, methodName=None):
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
       raise AttributeError('{} already defined in logging module'.format(levelName))
    if hasattr(logging, methodName):
       raise AttributeError('{} already defined in logging module'.format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
       raise AttributeError('{} already defined in logger class'.format(methodName))

    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)
    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)

def ropy_init():
    addLoggingLevel('TRACE', logging.DEBUG-5) # internal logging level

    parser = argparse.ArgumentParser(description='Rock Python initialization')
    parser.add_argument('--log_level', nargs='?', type=str, default='INFO',
                        help='set debug level, DEBUG | INFO | ERROR')
    args, unknown = parser.parse_known_args()
    log_lvl = logging.getLevelName(args.log_level)

    title = "[RockPy]"
    fmt = f"{title} %(levelname)s %(asctime)s %(threadName)s - %(message)s"
    datefmt = "%H:%M:%S"

    log = logging.getLogger("RockPy")
    
    fh = logging.FileHandler(filename='RoPy.log', mode='w', delay=True)
    fh.addFilter(LevelFilter(log_lvl))
    fh.setFormatter(CustFormatter(fmt=fmt, datefmt=datefmt))
    log.addHandler(fh)
    
    sh = logging.StreamHandler(sys.stdout)
    sh.addFilter(LevelFilter(log_lvl))
    sh.setFormatter(CustFormatter(fmt=fmt, datefmt=datefmt))
    log.addHandler(sh)
        
    log.setLevel(log_lvl)

    def exception_hook(exc_type, exc_val, exc_tb):
        log.error('\n'+''.join(traceback.format_exception(exc_type, exc_val, exc_tb)))
    sys.excepthook = exception_hook

ropy_init()


from RoPy.Pyst import *
from RoPy.Component import *
from RoPy.RAL import *
from RoPy import constraint
