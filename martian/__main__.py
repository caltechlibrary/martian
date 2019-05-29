'''
__main__: main command-line interface to Martian

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2019 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import os
import os.path as path
import plac
import sys
import time
from   threading import Thread
import traceback

import martian
from martian.control import MartianControlGUI, MartianControlCLI
from martian.debug import set_debug, log
from martian.exceptions import *
from martian.files import desktop_path, rename_existing, file_in_use
from martian.messages import MessageHandlerGUI, MessageHandlerCLI
from martian.network import network_available
from martian.progress import ProgressIndicatorGUI, ProgressIndicatorCLI
from martian.tind import search_and_download


# Main program.
# ......................................................................

@plac.annotations(
    output     = ('write results to the file R',                    'option', 'o'),
    start_at   = ("start with Nth record (default: start at 1)",    'option', 's'),
    total      = ('stop after processing M records (default: all)', 'option', 't'),
    no_color   = ('do not color-code terminal output',              'flag',   'C'),
    no_gui     = ('do not start the GUI interface (default: do)',   'flag',   'G'),
    version    = ('print version info and exit',                    'flag',   'V'),
    debug      = ('turn on debugging',                              'flag',   'Z'),
    search     = 'complete search URL (default: none)',
)

def main(output = 'O', start_at = 'N', total = 'M', no_color = False,
         no_gui = False, version = False, debug = False, *search):
    '''Martian: search caltech.tind.io and download MARC records.

Takes one required argument on the command line: the search query string.
The string should be a complete search URL as would be typed into a web
browser address bar (or more practically, copied from the browser address bar
after performing some exploratory searches in caltech.tind.io).  It is best
to quote the search string, using double quotes on Windows and single quotes
on Linux/Unix, to avoid terminal shells interpreting special characters such
as question marks in the search string.  Example (for Windows):

   martian "https://caltech.tind.io/search?ln=en&p=856%3A%27ebrary%27"

If given the -t option (/t on Windows), it will only fetch and process a
total of that many results instead of all results.  If given the -s (/s on
Windows) option, it will start at that entry instead of starting at number 1;
this is useful if searches are being done in batches or a previous search is
interrupted and you don't want to restart from 1.

If given an output file using the -o option (/o on Windows), the results will
be written to that file.  If no output file is specified, the output is
written to a file named "output.xml" on the user's desktop.  The results are
always MARC records in XML format.

This program will print information to the terminal as it runs, unless the
option -q (or /q on Windows) is given to make it more quiet.
'''

    # Our defaults are to do things like color the output, which means the
    # command line flags make more sense as negated values (e.g., "no-color").
    # However, dealing with negated variables in our code is confusing, so:
    use_color   = not no_color
    use_gui     = not no_gui

    # Process the version argument first, because it causes an early exit.
    if version:
        print('{} version {}'.format(martian.__title__, martian.__version__))
        print('Author: {}'.format(martian.__author__))
        print('URL: {}'.format(martian.__url__))
        print('License: {}'.format(martian.__license__))
        sys.exit()

    # Configure debug logging if it's turned on.
    if debug:
        set_debug(True)

    # We use default values that provide more intuitive help text printed by
    # plac.  Rewrite the values to things we actually use.
    if output == 'O':
        output = None
    if total and total == 'M':
        total = None
    if start_at and start_at == 'N':
        start_at = 1
    if search:
        search = search[0]

    # Switch between different ways of getting information from/to the user.
    if use_gui:
        controller = MartianControlGUI()
        notifier   = MessageHandlerGUI()
        tracer     = ProgressIndicatorGUI()
    else:
        controller = MartianControlCLI()
        notifier   = MessageHandlerCLI(use_color)
        tracer     = ProgressIndicatorCLI(use_color)

    # Start the worker thread.
    if __debug__: log('starting main body thread')
    controller.start(MainBody(output, total, start_at, search, debug,
                              controller, notifier, tracer))


class MainBody(Thread):
    '''Main body of Martian implemented as a Python thread.'''

    def __init__(self, output, total, start_at, search, debug,
                 controller, notifier, tracer):
        '''Initializes main thread object but does not start the thread.'''
        Thread.__init__(self, name = "MainBody")
        self._output     = output
        self._total      = total
        self._start_at   = start_at
        self._search     = search
        self._debug      = debug
        self._controller = controller
        self._tracer     = tracer
        self._notifier   = notifier
        if controller.is_gui:
            # Only make this a daemon thread when using the GUI; for CLI, it
            # must not be a daemon thread or else Martian exits immediately.
            self.daemon = True


    def run(self):
        # Set shortcut variables for better code readability below.
        output     = self._output
        total      = self._total
        start_at   = self._start_at
        search     = self._search
        debug      = self._debug
        controller = self._controller
        notifier   = self._notifier
        tracer     = self._tracer

        # Preliminary sanity checks.  Do this here because we need the notifier
        # object to be initialized based on whether we're using GUI or CLI.
        tracer.start('Performing initial checks')
        if not network_available():
            notifier.fatal('No network connection.')

        # If we get this far, we're ready to do this thing.
        try:
            if controller.is_gui:
                tracer.update('Asking user for input & output info')
                (search, output) = None, "/tmp/out.xml"
            elif not search:
                notifier.fatal('No search query string given.')
                tracer.stop('Quitting.')
                controller.stop()

            if not output:
                if __debug__: log('setting output file to default')
                output = path.join(desktop_path(), "output.xml")
            if path.exists(output):
                rename_existing(output)
            if file_in_use(output):
                details = '{} appears to be open in another program'.format(output)
                notifier.warn('Cannot write output file -- is it still open?', details)

            tracer.update('Downloading results from caltech.tind.io')
            search_and_download(search, output)
            tracer.update('Done. Output is in {}'.format(output))
        except (KeyboardInterrupt, UserCancelled) as err:
            tracer.stop('Quitting.')
            controller.stop()
        except ServiceFailure:
            tracer.stop('Stopping due to a problem connecting to services')
            controller.stop()
        except Exception as err:
            if debug:
                import pdb; pdb.set_trace()
            tracer.stop('Stopping due to error')
            notifier.fatal(martian.__title__ + ' encountered an error',
                           str(err) + '\n' + traceback.format_exc())
            controller.stop()
        else:
            tracer.stop('Done')
            controller.stop()


# On windows, we want the command-line args to use slash intead of hyphen.

if sys.platform.startswith('win'):
    main.prefix_chars = '/'


# Main entry point.
# ......................................................................
# The following allows users to invoke this using "python3 -m martian".

if __name__ == '__main__':
    plac.call(main)


# For Emacs users
# ......................................................................
# Local Variables:
# mode: python
# python-indent-offset: 4
# End:
