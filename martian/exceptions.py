'''
exceptions.py: exceptions defined by Martian

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2019-2021 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

class UserCancelled(Exception):
    '''The user elected to cancel/quit the program.'''
    pass

class ServiceFailure(Exception):
    '''Unrecoverable problem involving network services.'''
    pass

class NoContent(Exception):
    '''Server returned a code 401 or 404, indicating no content found.'''

class RateLimitExceeded(Exception):
    '''The service flagged reports that its rate limits have been exceeded.'''
    pass

class InternalError(Exception):
    '''Unrecoverable problem involving Martian itself.'''
    pass

class RequestError(Exception):
    '''Problem with the TIND query or request.'''
    pass
