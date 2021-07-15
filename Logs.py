import logging


def log(name, msg, loglvl='WARNING'):
    """Logs info, warnings, errors and criticals
    for the current directory for traceability.
    The file is 'Logs.log'

    Parameters:
        name (str): The class (or function) name
        msg (str): The message to be logged
        loglvl (str): {'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
    """

    FILENAME = 'Logs.log'
    LOGFORMAT = r'%(asctime)s,%(name)s,%(levelname)s: %(message)s'
    DATEFMT = r'%Y-%m-%d %H:%M'
    loglvl = loglvl.upper()
    loglevel = getattr(logging, loglvl)

    logging.basicConfig(filename=FILENAME,
                        format=LOGFORMAT,
                        datefmt=DATEFMT,
                        level=loglevel)
    logger = logging.getLogger(name)

    if loglvl == 'INFO':
        logger.info(msg)
    elif loglvl == 'WARNING':
        logger.warning(msg)
    elif loglvl == 'ERROR':
        logger.error(msg)
    elif loglvl == 'CRITICAL':
        logger.critical(msg)


if __name__ == '__main__':
    log()


###################### ARCHIVED #####################

# def error_log(e, file_name):
#     """Loggar villuskilabod i sjalfvirkum keyrslum"""

#     import csv
#     import time

#     dt_raw = time.gmtime()
#     dt = time.strftime(r"%Y-%m-%d %H:%M:%S", dt_raw)
#     with open("Error_Log.log",
#               mode='a') as my_text_file:
#         # Skrifum i text-file
#         error_writer = csv.writer(my_text_file,
#                                   delimiter=";",
#                                   lineterminator="\n")
#         error_writer.writerow([dt, file_name, e])
#     return
