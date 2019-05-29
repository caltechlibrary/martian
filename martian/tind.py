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

from pycurl import Curl

import martian
from martian.debug import log


# Functions.
# .............................................................................

def search_and_download(search, output):
    import pdb; pdb.set_trace()
    with open(output, 'wb') as out:
        curl = Curl()
        curl.setopt(curl.URL, search)
        curl.setopt(curl.WRITEDATA, out)
        curl.perform()
        curl.close()
