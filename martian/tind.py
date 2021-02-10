'''
tind.py: Martian code for interacting with Caltech.TIND.io

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2019-2021 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from   bs4 import BeautifulSoup
import certifi
import humanize
from   lxml import html
from   pubsub import pub
import pycurl
from   pycurl import Curl
import re
from   threading import Thread
import urllib.parse
try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO

if __debug__:
    from sidetrack import log, logr

import martian
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

    def __init__(self, controller, notifier, tracer):
        self._controller  = controller
        self._notifier    = notifier
        self._tracer      = tracer
        self._stop        = False
        self._downloader  = None
        self._num_written = 0


    def download(self, search, output, start = 1, total = -1):
        '''Search with the given 'search' string and write the output to file
        named by 'output'.  Get 'total' number of records (default: all),
        optionally starting from record number 'start' (default: 1).
        Returns the number of records downloaded, or 0 if something went wrong.
        '''
        tracer   = self._tracer
        notifier = self._notifier

        if not search:
            tracer.update('Given an empty search string -- nothing to do')
            return 0
        elif search.startswith('http'):
            # We were given a full url.  Extract just the search part.
            match = re.search(r'p=([^&]+)', search)
            query = match.group(1) if match is not None else ""
        else:
            # We were given a search expression directly.  Quote it to deal
            # with embedded spaces and whatnot.
            query = urllib.parse.quote(search)

        # Look for any collections that might be specified.
        collections = []
        if search.find('&c'):
            # There can be more than one.
            for match in re.finditer(r'&c=([^&]+)', search):
                collections.append(match.group(1))

        # TIND doesn't seem to offer a way to find out the number of expected
        # records if you ask for MARC XML output.  So here we start by doing
        # a normal TIND search and parsing the HTML to look for the total
        # results it reports, then loop to get the MARC records.

        tracer.update('Asking caltech.tind.io how many records to expect')
        prelim_search = url_for_get(query, collections, get = 1, start = 1, marc = False)
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
        if tds == []:
            notifier.info('This TIND search produced 0 records')
            return 0

        # When multiple collections are used, the total number of records is
        # the sum of the results from individual collections.
        num_records = 0
        for td in tds:
            if td.text.find('records found') > 0:
                match = re.search('([0-9,]+) records found', td.text)
                if match and match.group(1):
                    num_records += int(match.group(1).replace(',', ''))
                else:
                    notifier.fatal('Unexpected format for number of records')
                    raise InternalError(details)

        if num_records == 0:
            notifier.info('This TIND search produced 0 records')
            return 0
        else:
            text_number = humanize.intcomma(num_records)
            tracer.update('This search will produce {} records'.format(text_number))

        # OK, now let's loop.
        self._downloader = Thread(target = self._download_loop,
                                  args = (query, collections, output, start,
                                          total, num_records, tracer))
        if __debug__: log('starting downloader thread')
        self._downloader.start()
        if __debug__: log('waiting on downloader thread')
        self._downloader.join()
        if __debug__: log('downloader thread has returned')

        # Return how many records ended up being written.
        return self._num_written


    def interrupt(self):
        if __debug__: log('setting the stop flag')
        self._stop = True
        if self._downloader:
            if __debug__: log('waiting on downloader thread')
            self._downloader.join()
            if __debug__: log('downloader thread has returned')


    def _download_loop(self, query, collections, output, start, total, num_records, tracer):
        if total < 0:
            total = num_records
        if __debug__: log('opening output file: {}', output)
        out = open(output, 'wb')
        out.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        out.write(b'<collection xmlns="http://www.loc.gov/MARC21/slim">\n')

        while start <= total and not self._stop:
            # The value of end_at is only used for the user message.
            if start + _RECORDS_PER_GET > num_records:
                end_at = num_records
            else:
                end_at = _RECORDS_PER_GET + start - 1
            tracer.update('Getting records {} to {}'.format(start, end_at))
            data = None
            try:
                url = url_for_get(query, collections, _RECORDS_PER_GET, start, marc = True)
                data = BytesIO()
                curl = Curl()
                curl.setopt(pycurl.CAINFO, certifi.where())
                curl.setopt(curl.URL, url)
                curl.setopt(curl.WRITEDATA, data)
                if __debug__: log('curling "{}"', url)
                curl.perform()
                curl.close()
            except Exception as err:
                if __debug__: log('exception in curl process: {}', str(err))
                tracer.update('Stopping download due to problem')
                data = None
                raise err

            if data:
                # Skip stuff at beginning and end, and write to the file.
                v = data.getvalue()
                block_start = v.find(b'<collection xmlns="http://www.loc.gov/MARC21/slim">')
                block_end = v.rfind(b'</collection>')
                out.write(v[block_start + 52 : block_end])

                # Increment and continue to get more
                start += _RECORDS_PER_GET
                self._num_written = end_at

        if __debug__: log('closing output due to interruption' if self._stop
                          else 'closing output file')
        out.write(b'</collection>\n')
        out.close()


# Miscellaneous utility functions.
# .............................................................................

def url_for_get(search_string, collections, get, start, marc = False):
    u = (_BASE_GET_URL
            + ('&c=' + '&c='.join(collections) if collections else '')
            + '&p=' + search_string
            + '&jrec=' + str(start)
            + '&rg=' + str(get)
            + ('&of=xm' if marc else ''))
    return u
