import logging
import logging.handlers
import socket
import sys

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict

try:
    import codecs
except ImportError:
    codecs = None

import datetime


NILVALUE = '-'

#As defined in RFC5424 Section 7
STRUCTURED_DATA_IDs = ('timeQuality', 'origin', 'meta')

#Version of the protocol we support
SYSLOG_VERSION=1


class FullSysLogHandler(logging.handlers.SysLogHandler):
    """An RFC 5425-complaint Syslog Handler for the python logging framework"""
    
    def __init__(self, address=('localhost', logging.handlers.SYSLOG_UDP_PORT),
                 facility=logging.handlers.SysLogHandler.LOG_USER, socktype=socket.SOCK_DGRAM,
                 hostname=None, appname=None, procid=None, 
                 msgid=None, structured_data=OrderedDict(), enterprise_id=None):

        self.hostname, self.appname, self.procid = hostname, appname, procid
        self.msgid, self.structured_data, self.enterprise_id = msgid, structured_data, enterprise_id

        if self.hostname is None:
            self.hostname = socket.gethostname()

        if self.appname is None:
            self.appname = sys.argv[0]

        if self.procid is None:
            self.procid = NILVALUE

        if self.msgid is None:
            self.msgid = NILVALUE

        return super(FullSysLogHandler, self).__init__(address, facility, socktype)

    def get_hostname(self, record):
        return getattr(record, 'hostname', self.hostname)

    def get_appname(self, record):
        return getattr(record, 'appname', self.appname)

    def get_procid(self, record):
        return getattr(record, 'procid', self.procid)

    def get_msgid(self, record):
        return getattr(record, 'msgid', self.msgid)

    def get_enterprise_id(self, record):
        return getattr(record, 'enterprise_id', self.enterprise_id)

    def get_structured_data(self, record):
        structured_data = OrderedDict()
        structured_data.update(self.structured_data)
        structured_data.update(getattr(record, 'structured_data', {}))
        return structured_data

    def emit(self, record):
        """
        Emit a record.

        The record is formatted, and then sent to the syslog server. If
        exception information is present, it is NOT sent to the server.
        """
        #Prepare the message.

        #First the priority:
        pri = '<%d>%d' % (self.encodePriority(self.facility,
                                            self.mapPriority(record.levelname)),
                            SYSLOG_VERSION)

        #Let's map some extra stuff, and clean it up to max values
        hostname = self.get_hostname(record).encode('ascii', 'replace')[:255]
        appname = self.get_appname(record).encode('ascii', 'replace')[:48]
        procid = self.get_procid(record).encode('ascii', 'replace')[:128]
        msgid = self.get_msgid(record).encode('ascii', 'replace')[:32]
        enterprise_id = self.get_enterprise_id(record)
        
        structured_data = self.get_structured_data(record)

        #Clean up the structured data
        for key, value in list(structured_data.items()):
            #we ask for the list so we can change the keys

            if isinstance(value, dict):
                value = value.items()
            newvals = []
            for (itemkey, itemvalue) in value:
                itemkey = itemkey.encode('ascii', 'replace').replace('"','').replace(' ', '').replace(']', '').replace('=', '')[:32]
                itemvalue = itemvalue.encode('utf8', 'replace').replace('\\', '\\\\').replace('"', '\\"').replace(']','\\]')
                newvals.append('%s="%s"' % (itemkey, itemvalue))

            structured_data[key] = ' '.join(newvals)

            if key not in STRUCTURED_DATA_IDs and enterprise_id is not None and '@' not in key:
                newkey = '%s@%s' % (key, enterprise_id)
            else:
                newkey = key
                newkey = newkey.encode('ascii', 'replace').replace('"','').replace(' ', '').replace(']', '').replace('=', '')[:32]
                
            if newkey != key:    
                structured_data[newkey] = structured_data[key]
                del structured_data[key]

        msg = self.format(record)
        if isinstance(msg, unicode):
            msg = msg.encode('utf-8')
            if codecs:
                msg = codecs.BOM_UTF8 + msg

        ts = datetime.datetime.fromtimestamp(record.created)
        #NEED TO DEAL WITH TIME ZONES
        timestamp = ts.isoformat()

        header = ' '.join((pri, timestamp, hostname, appname, procid, msgid))

        if structured_data:
            sd = ''.join('[%s]' % (' '.join((key, value))) for key, value in structured_data.items())
        else:
            sd = NILVALUE

        msg = ' '.join((header, sd, msg))

        msg = ''.join((msg, '\000'))

        #This section copied from logging.SyslogHandler
        try:
            if self.unixsocket:
                try:
                    self.socket.send(msg)
                except socket.error:
                    self._connect_unixsocket(self.address)
                    self.socket.send(msg)
            elif self.socktype == socket.SOCK_DGRAM:
                self.socket.sendto(msg, self.address)
            else:
                self.socket.sendall(msg)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)