'''
__main__: main command-line interface to Martian

Martian searches caltech.tind.io and downloads the results as MARC XML records.

Martian can be run as either a command-line application or a GUI application.
By default, Martian starts a GUI to get information from the user and tell
the user about progress while it runs.  If given the -G option (/G on Windows),
it does not start the GUI.

When running without the GUI, Martian takes one required argument on the
command line: the query string to use for the search in TIND.  Alternatively,
the command-line argument can be a complete search URL as would be typed into
a web browser (or more practically, copied from the browser address bar after
performing some exploratory searches in caltech.tind.io).  It is best to
quote the search string, using double quotes on Windows and single quotes on
Linux/Unix, to avoid terminal shells interpreting special characters such as
question marks in the search string.  Example (for Windows):

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

If given the -Z option (/Z on Windows), this program will print a trace of
what it is doing to the terminal window, and will also drop into a debugger
upon the occurrence of any errors.  This can be useful for debugging.
The option -C (/C on Windows) is useful when running with -Z to avoid the
default behavior of color-coding the output, so that the combination of
debugging messages and normal messages is more easily readable.

If given the -V option (/V on Windows), this program will print version
information and exit without doing anything else.

If given the -h option (/h on Windows), this program will print help
information and exit without doing anything else.

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
from   pubsub import pub
from   queue import Queue
import sys
import time
from   threading import Thread
import traceback
import wx

import martian
from martian.control import MartianControlGUI, MartianControlCLI
from martian.debug import set_debug, log
from martian.exceptions import *
from martian.files import desktop_path, rename_existing, file_in_use
from martian.messages import MessageHandlerGUI, MessageHandlerCLI
from martian.network import network_available
from martian.progress import ProgressIndicatorGUI, ProgressIndicatorCLI
from martian.tind import Tind


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
    search     = 'search string or complete search URL (default: none)',
)

def main(output = 'O', start_at = 'N', total = 'M', no_color = False,
         no_gui = False, version = False, debug = False, *search):
    '''Search caltech.tind.io and download the results as MARC XML records.

Martian can be run as either a command-line application or a GUI application.
By default, Martian starts a GUI to get information from the user and tell
the user about progress while it runs.  If given the -G option (/G on Windows),
it does not start the GUI.

When running without the GUI, Martian takes one required argument on the
command line: the query string to use for the search in TIND.  Alternatively,
the command-line argument can be a complete search URL as would be typed into
a web browser (or more practically, copied from the browser address bar after
performing some exploratory searches in caltech.tind.io).  It is best to
quote the search string, using double quotes on Windows and single quotes on
Linux/Unix, to avoid terminal shells interpreting special characters such as
question marks in the search string.  Example (for Windows):

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

If given the -Z option (/Z on Windows), this program will print a trace of
what it is doing to the terminal window, and will also drop into a debugger
upon the occurrence of any errors.  This can be useful for debugging.
The option -C (/C on Windows) is useful when running with -Z to avoid the
default behavior of color-coding the output, so that the combination of
debugging messages and normal messages is more easily readable.

If given the -V option (/V on Windows), this program will print version
information and exit without doing anything else.

If given the -h option (/h on Windows), this program will print this help
message and exit without doing anything else.
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
        total = -1
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
    controller.run(MainBody(output, total, start_at, search, debug,
                            controller, notifier, tracer))


class MainBody(Thread):
    '''Main body of Martian implemented as a Python thread.'''

    def __init__(self, output, total, start_at, search, debug,
                 controller, notifier, tracer):
        '''Initializes main thread object but does not start the thread.'''
        Thread.__init__(self, name = "MainBody")
        if controller.is_gui:
            # Only make this a daemon thread when using the GUI; for CLI, it
            # must not be a daemon thread or else Martian exits immediately.
            self.daemon = True
        self._output     = output
        self._total      = total
        self._start_at   = start_at
        self._search     = search
        self._debug      = debug
        self._controller = controller
        self._tracer     = tracer
        self._notifier   = notifier
        self._tind       = Tind(controller, notifier, tracer)


    def run(self):
        '''Implementation of Thread object run() method.'''

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
        if not controller.is_gui and not search:
            notifier.fatal('No search query string given.')
            tracer.stop('Quitting.')
            controller.quit()

        # If we get this far, we're ready to do this thing.
        written = 0
        try:
            cancelled = False
            if controller.is_gui:
                tracer.update('Asking user for input & output info')
                (search, output, cancelled) = self.get_user_input(search, output)
                if __debug__: log('search string: {}', search)
                if __debug__: log('setting output to {}', output)
            if cancelled:
                if __debug__: log('user cancelled; raising UserCancelled')
                tracer.update('Input cancelled by user; stopping')
                raise UserCancelled
            if not search:
                if __debug__: log('No search string given; raising UserCancelled')
                tracer.update('No search string given -- nothing to do')
                raise UserCancelled
            if not output:
                output = path.join(desktop_path(), "output.xml")
                tracer.update('No output file specified; using {}'.format(output))

            if not output.endswith('.xml'):
                output += '.xml'
            if path.exists(output):
                rename_existing(output)
            if file_in_use(output):
                details = '{} appears to be open in another program'.format(output)
                notifier.warn('Cannot write output file -- is it still open?', details)

            tracer.update('Beginning interaction with caltech.tind.io')
            written = self._tind.download(search, output, start_at, total)
            tracer.update('{} records written to {}'.format(written, output))
        except (KeyboardInterrupt, UserCancelled) as err:
            # If using the GUI and the user deliberately quit in the input
            # dialog, we stop what we're doing and leave it to the user to
            # click the final 'quit' button on the main application in case
            # they want to use the help.  In cmd-line mode, we just quit now.
            if not controller.is_gui:
                tracer.stop('Quitting.')
                self._tind.interrupt()
                controller.quit()
        except ServiceFailure:
            tracer.stop('Stopping due to a problem connecting to services')
            controller.quit()
        except Exception as err:
            if debug:
                import pdb; pdb.set_trace()
            tracer.stop('Stopping due to error')
            notifier.fatal(martian.__title__ + ' encountered an error',
                           str(err) + '\n' + traceback.format_exc())
            controller.quit()
        else:
            tracer.stop('Done')
            if controller.is_gui:
                notifier.info('Done. {} records written to {}'.format(written, output))
            # Don't stop the controller if we reach the end normally, so that
            # the user can see the trace after the program finishes.


    def stop(self):
        '''Stop execution of processes.  This is called by our controller.'''
        self._tind.interrupt()


    def get_user_input(self, search, output):
        results = Queue()
        if __debug__: log('sending message to user_dialog')
        wx.CallAfter(pub.sendMessage, "user_dialog", results = results,
                     search = search, output = output)
        if __debug__: log('blocking to get results')
        results_tuple = results.get()
        if __debug__: log('user input obtained')
        # Results will be a tuple of user, password, cancelled
        return results_tuple


# On windows, we want the command-line args to use slash instead of hyphen.

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
