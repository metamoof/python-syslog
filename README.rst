=============== 
 Python-Syslog
===============

-----------------------------------------------------------------------
 An RFC 5424-complaint Syslog Handler for the Python Logging Framework
-----------------------------------------------------------------------

Wait, doesn't Python already have a Syslog Handler?
---------------------------------------------------

Python_ has `python.logging.handlers.SysLogHandler`_- however, this is not a full implementation of the Syslog Format (as documented in RFC5424_), and leaves the programmer to try and work out the full correct format using a formatter.

Also, Python's SysLogHandler does not handle UTF8 correctly according to the spec. This was reported in `Issue 1442`_ and a `fix was applied`_ but that leaves it entirely in the hands of the programmer to correctly format the string.

This project aims to facilitate sending well-formed and correct Syslog messages.

.. _Python: http://www.python.org/
.. _python.logging.handlers.SysLogHandler: http://docs.python.org/2/library/logging.handlers.html#sysloghandler
.. _RFC5424: http://tools.ietf.org/html/rfc5424
.. _Issue 1442: http://bugs.python.org/issue14452
.. _fix was applied: http://bugs.python.org/issue14452#msg158447