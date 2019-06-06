'''
tind.py: Martian code for interacting with Caltech.TIND.io

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2019 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from   bs4 import BeautifulSoup
import certifi
import humanize
from   lxml import html
import pycurl
from   pycurl import Curl
import re
import urllib.parse
try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO

import martian
from martian.debug import log
from martian.exceptions import *
from martian.network import net


# Global constants.
# .............................................................................

# Some testing with caltech.tind.io reveals that if you ask for more than 200,
# it returns 200.

_RECORDS_PER_GET = 200
'''
Number of records to request from TIND at each iteration.  The maximum allowed
by TIND is 200.
'''

_BASE_GET_URL = 'https://caltech.tind.io/search?ln=en'
'''
URL fragment common to all our search + download calls.
''' 


# Main class.
# .............................................................................

class Tind(object):

    def __init__(self, controller, notifier, tracer, debug = False):
        self._controller = controller
        self._notifier   = notifier
        self._tracer     = tracer
        self._debug      = debug


    def search_and_download(self, search, output, start_at = 1, total = -1):
        '''Search with the given 'search' string and write the output to file
        named by 'output'.  Get 'total' number of records (default: all),
        optionally starting from record number 'start_at' (default: 1).
        Returns the number of records downloaded, or 0 if something went wrong.
        '''
        tracer   = self._tracer
        notifier = self._notifier
        debug    = self._debug

        if not search:
            tracer.update('Given an empty search string -- nothing to do')
            return 0
        elif search.startswith('http'):
            # We were given a full url.  Extract just the search part.
            match = re.search('p=([^&]+)', search)
            query = match.group(1)
        else:
            # We were given just the search expression.
            query = search

        # TIND doesn't seem to offer a way to find out the number of expected
        # records if you ask for MARC XML output.  So here we start by doing
        # a normal format TIND search and parsing the HTML to look for the
        # total results it reports, then loop to get the MARC records.

        tracer.update('Asking caltech.tind.io how many records to expect')
        prelim_search = url_for_get(query, num_get = 1, start_at = 1, marc = False)
        (response, error) = net('get', prelim_search)
        if response.status_code > 300:
            details = 'exception connecting to tind.io: {}'.format(error)
            notifier.fatal('Failed to connect to tind.io -- try again later', details)
            raise ServiceFailure(details)
        if error:
            details = 'exception: {}'.format(error)
            notifier.fatal('Failed to search TIND', details)
            raise RequestError(details)
        soup = BeautifulSoup(response.content, features='lxml')
        tds = soup.select('.searchresultsboxheader')
        if not tds or len(tds) != 3:
            details = 'TIND results page was not in the expectd format'
            notifier.fatal('Received unexpected content from TIND', details)

        # The 2nd <td> of class 'searchresultsboxheader' contains the number.
        match = re.search('<span><strong>([0-9,]+)</strong> records found', str(tds[1]))
        if match and match.group(1):
            num_records = int(match.group(1).replace(',', ''))
        else:
            notifier.fatal('Unexpected result from TIND: could not find number of records')
            raise InternalError(details)
        if num_records == 0:
            notifier.info('This TIND search produced 0 records')
            return 0
        else:
            text_number = humanize.intcomma(num_records)
            tracer.update('The search will produce {} records'.format(text_number))

        # OK, now let's loop.
        if total < 0:
            total = num_records
        error = None
        out = None
        num_written = 0
        try:
            out = open(output, 'wb')
            out.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
            out.write(b'<collection xmlns="http://www.loc.gov/MARC21/slim">\n')

            while start_at < total and not error:
                # The value of end_at is only used for the user message.
                if start_at + _RECORDS_PER_GET > num_records:
                    end_at = num_records
                else:
                    end_at = _RECORDS_PER_GET + start_at - 1
                tracer.update('Getting records {} to {}'.format(start_at, end_at))
                data = None
                try:
                    url = url_for_get(query, _RECORDS_PER_GET, start_at, marc = True)
                    data = BytesIO()
                    curl = Curl()
                    curl.setopt(pycurl.CAINFO, certifi.where())
                    curl.setopt(curl.URL, url)
                    curl.setopt(curl.WRITEDATA, data)
                    curl.perform()
                    curl.close()
                except Exception as err:
                    if __debug__: log('Exception in curl process: {}', str(err))
                    tracer.update('Stopping download due to problem')
                    data = None
                    raise err

                if data:
                    # Skip stuff at beginning and end, and write to the file.
                    v = data.getvalue()
                    start = v.find(b'<collection xmlns="http://www.loc.gov/MARC21/slim">')
                    end = v.rfind(b'</collection>')
                    out.write(v[start + 52 : end])

                    # Increment and continue to get more
                    start_at += _RECORDS_PER_GET
                    num_written = end_at
            if __debug__: log('download loop finished normally')
        finally:
            if __debug__: log('closing output file')
            if out:
                out.write(b'</collection>')
                out.close()
        return num_written


# Miscellaneous utility functions.
# .............................................................................

def url_for_get(search_string, num_get, start_at, marc = False):
    return (_BASE_GET_URL
            + '&p=' + urllib.parse.quote(search_string)
            + '&jrec=' + str(start_at)
            + '&rg=' + str(num_get)
            + ('&of=xm' if marc else ''))
