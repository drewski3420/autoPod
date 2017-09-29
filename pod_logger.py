import logging

def setup_custom_logger(name):
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('chardet').setLevel(logging.WARNING)
    
    path = 'configs/autopod.log'
    formatter = logging.Formatter(fmt='%(asctime)s | %(name)s | %(levelname)-8s | %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler(path, mode='a',encoding = 'UTF-8')
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger
