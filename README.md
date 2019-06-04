Martian<img width="12%" align="right" src=".graphics/martian-logo.svg">
=======

_Martian_ searches Caltech's TIND.io database with a user-specified query and downloads the MARC XML records produced. The name "Martian" is a loose acronym for _**<ins>MAR</ins>C from <ins>TI</ins>ND <ins>A</ins>ssista<ins>n</ins>t**_.

*Authors*:      [Michael Hucka](http://github.com/mhucka)<br>
*Repository*:   [https://github.com/caltechlibrary/martian](https://github.com/caltechlibrary/martian)<br>
*License*:      BSD/MIT derivative &ndash; see the [LICENSE](LICENSE) file for more information

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg?style=flat-square)](https://choosealicense.com/licenses/bsd-3-clause)
[![Python](https://img.shields.io/badge/Python-3.4+-brightgreen.svg?style=flat-square)](http://shields.io)
[![Latest release](https://img.shields.io/badge/Latest_release-1.0.0-b44e88.svg?style=flat-square)](http://shields.io)


Table of Contents
-----------------
* [Introduction](#-introduction)
* [How to install and uninstall Martian](#-installation-instructions)
* [How to use Martian](#︎-basic-operation)
* [Getting help and support](#-getting-help-and-support)
* [Do you like it?](#-do-you-like-it)
* [Acknowledgments](#︎-acknowledgments)
* [Copyright and license](#︎-copyright-and-license)


☀ Introduction
-----------------------------

Caltech's librarians occasionally need to download large numbers of records from Caltech's TIND.io database.  Doing this through TIND's web interface is tedious because TIND.io does not provide a bulk download facility.  _Martian_ is a program to make this work easier.  It performs one simple task: run a query in caltech.tind.io and download all the results in MARC XML format to a file on the local computer.


✺ How to install and uninstall Martian
-------------------------------------

### Using the normal installer program

The developers provide an installer program for Caltech Library users.  Please contact the developers to get a copy of the installer program for Windows 7, Windows 10, or macOS 10.12+.  Note also that installation of _Martian_ on Windows requires administrator priviledges.

To uninstall _Martian_ on a Windows 10 system, use the normal Windows **Add or remove programs** facility in the **Systems Settings** panel.


### Using the source code repository

Alternatively, you can also download the source code for Martian and run it directly using a Python interpreter.  The following is probably the simplest and most direct way to install this software on your computer:
```sh
sudo python3 -m pip install git+https://github.com/caltechlibrary/martian.git --upgrade
```

Alternatively, you can clone this GitHub repository and then run `setup.py`:
```sh
git clone https://github.com/caltechlibrary/martian.git
cd martian
sudo python3 -m pip install . --upgrade
```


▶︎ How to use Martian
--------------------

Martian is simple in operation and has a correspondingly simple interface. The interface has two modes of operation: using a graphical user interface (GUI), or using the command-line.

When installed on a Windows system using the installer provided by the developers, Martian only has a GUI interface and will always run in GUI mode.  When installed using the Python module installation method on Linux, macOS or Windows, Martian also provides a simple command-line interface program called `martian`.  Martian can then be invoked by running `martian` from a terminal emulator program or, alternatively, using `python -m martian` (assuming your `python` is Python version 3).

### Running Martian using the GUI interface

On Windows or other environment where the GUI version of Martian is available, start Martian normally as you would any other program (e.g., by double-clicking Martian's program icon).



### Running Martian using the command-line interface

For help with usage at any time, run `martian` with the option `-h` (or `/h` on Windows).

By default, the command-line interface will start a GUI to get information from the user and tell the user about progress while it runs.  If given the `-G` option (`/G` on Windows), it does not start the GUI.

When running without the GUI, Martian takes one required argument on the command line: the query string to use for the search in TIND.  Alternatively, the command-line argument can be a complete search URL as would be typed into a web browser (or more practically, copied from the browser address bar after performing some exploratory searches in caltech.tind.io).  It is best to quote the search string, using double quotes on Windows and single quotes on Linux/Unix, to avoid terminal shells interpreting special characters such as question marks in the search string.  Example (for Windows):

```
martian "https://caltech.tind.io/search?ln=en&p=856%3A%27ebrary%27"
```

If given the `-t` option (`/t` on Windows), it will only fetch and process a total of that many results instead of all results.  If given the `-s` (`/s` on Windows) option, it will start at that entry instead of starting at number 1; this is useful if searches are being done in batches or a previous search is interrupted and you don't want to restart from 1.

If given an output file using the `-o` option (`/o` on Windows), the results will be written to that file.  If no output file is specified, the output is written to a file named `output.xml` on the user's desktop.  The results are always MARC records in XML format.

If given the `-Z` option (`/Z` on Windows), this program will print a trace of what it is doing to the terminal window, and will also drop into a debugger upon the occurrence of any errors.  This can be useful for debugging.  The option `-C` (`/C` on Windows) is useful when running with `-Z` to avoid the default behavior of color-coding the output, so that the combination of debugging messages and normal messages is more easily readable.

If given the `-V` option (`/V` on Windows), this program will print version information and exit without doing anything else.


⁇ Getting help and support
--------------------------

If you find an issue, please submit it in [the GitHub issue tracker](https://github.com/caltechlibrary/martian/issues) for this repository.


☺︎ Acknowledgments
-----------------------

The [vector artwork](https://thenounproject.com/search/?q=martian&i=63049) of an alien spaceship used as a starting point for the logo for this repository was created by [Gonzalo Bravo](https://thenounproject.com/webposible/) for the [Noun Project](https://thenounproject.com).  It is licensed under the Creative Commons [Attribution 3.0 Unported](https://creativecommons.org/licenses/by/3.0/deed.en) license.  The vector graphics was modified by Mike Hucka to change the color.


☮︎ Copyright and license
---------------------

Copyright (C) 2019, Caltech.  This software is freely distributed under a BSD/MIT type license.  Please see the [LICENSE](LICENSE) file for more information.
    
<div align="center">
  <a href="https://www.caltech.edu">
    <img width="100" height="100" src=".graphics/caltech-round.svg">
  </a>
</div>
