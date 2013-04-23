#encoding:utf8

import logging
import syslog

logger = logging.getLogger()
data = dict(appname='Anothertest', procid='P12345', msgid='TESTER', structured_data={'foo@31456':(('bar', 'baz'),)})
sl = syslog.FullSysLogHandler(address=('logs.papertrailapp.com', 62756), **data)
sl2 = syslog.FullSysLogHandler(address=('127.0.0.1', 5005), **data)
logger.setLevel(logging.INFO)
logger.addHandler(sl)
logger.addHandler(sl2)
logger.info(u'€xtended Test')