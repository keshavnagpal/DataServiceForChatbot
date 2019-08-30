import logging
import time

def logger(*args):
	logging.basicConfig(filename='ApplicationLogs.log',level=logging.DEBUG,format='%(asctime)s %(message)s',datefmt='%x %X')
	logInfo=''
	for arg in args:
		logInfo+=str(arg)
	logging.debug("%s",logInfo)

def clearLog():
	with open('ApplicationLogs.log', 'w'):
		pass

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            logger('%r  %2.2f ms' % \
                  (method.__name__, (te - ts) * 1000))
        return result
    return timed