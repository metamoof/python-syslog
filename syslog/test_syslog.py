#encoding:utf8

import syslog
import unittest
import threading
import logging
import socket
import codecs
from test.test_logging import LogRecordSocketReceiver, LogRecordStreamHandler

class SyslogRecordHandler(LogRecordStreamHandler):
    def setup(self):
        self.textbuffer = ''
        return LogRecordStreamHandler.setup(self)

    def handle(self):
        text = self.connection.recv(16384)
        text = self.textbuffer + text
        lines = list(text.split('\x00'))
        self.textbuffer = lines[-1] #Should be '' if it ends in \000
        del lines[-1]

        for line in lines:
            if self.TCP_LOG_END in line:
                self.server.abort = True
                return
            self.server.log_output.append(line)

class SyslogSocketReceiver(LogRecordSocketReceiver):
    """ A Dummy TCP socket receiver """

    def __init__(self, host='localhost', port=0, handler=SyslogRecordHandler):
        LogRecordSocketReceiver.__init__(self, host, port, handler)
        self.log_output = []

class BaseSyslogTest(unittest.TestCase):

    def setUp(self):
        self.tcpserver = SyslogSocketReceiver()
        self.address = self.tcpserver.socket.getsockname()
        self.threads = [
                threading.Thread(target=self.tcpserver.serve_until_stopped)]
        for thread in self.threads:
            thread.start()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.handler = syslog.FullSysLogHandler(address=self.address, socktype=socket.SOCK_STREAM, **self.handlerattrs)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.INFO)

    def tearDown(self):
        self.tcpserver.abort = True
        del self.tcpserver
        for thread in self.threads:
            thread.join(2.0)
        self.logger.removeHandler(self.handler)
        self.handler.close()


    def get_output(self):
        """Get the log output as received by the TCP server."""
        # Signal the TCP receiver and wait for it to terminate.
        self.logger.critical(LogRecordStreamHandler.TCP_LOG_END)
        self.tcpserver.finished.wait(2.0)
        result = []
        for line in self.tcpserver.log_output:
            privers, timestamp, hostname, appname, procid, msgid, data = line.split(' ', 6)
            vers = privers[-1]
            pri = privers[:-1]
            if data[0] == '-':
                msg = data[2:]
                structured_data = {}
            else:
                #handle structured_data properly later
                pass
            result.append({
                'priority': pri,
                'version': vers,
                'timestamp': timestamp,
                'hostname': hostname,
                'appname': appname,
                'procid': procid,
                'msgid': msgid,
                'structured_data': structured_data,
                'message': msg,
                'line': line,
                })
        return result


class StrAndUnicode(BaseSyslogTest):
    handlerattrs = {}

    def test_strreceived(self):
        self.logger.info("Test str")

        lines = self.get_output()

        self.assertEquals(len(lines),1)
        self.assertIn("Test str", lines[0]['message'])
        self.assert_(not lines[0]['message'].startswith(codecs.BOM_UTF8))

    def test_unicodereceived(self):
        line1 = u"A pound sign: #"
        line2 = u"Another pound sign: \xA3"
        self.logger.info(line1)
        self.logger.info(line2)

        lines = self.get_output()

        self.assertEquals(len(lines),2)
        self.assert_(lines[0]['message'].startswith(codecs.BOM_UTF8))
        self.assert_(lines[1]['message'].startswith(codecs.BOM_UTF8))
        self.assertEquals(lines[0]['message'].decode('utf8')[1:], line1)
        self.assertEquals(lines[1]['message'].decode('utf8')[1:], line2)





if __name__ == '__main__':
    unittest.main()

