Martian<img width="12%" align="right" src=".graphics/martian-logo.svg">
=======

_Martian_ searches Caltech's TIND.io database with a user query and downloads the MARC records produced. The name "Martian" is a loose acronym for _**<ins>MAR</ins>C from <ins>TI</ins>ND <ins>A</ins>ssista<ins>n</ins>t**_.

*Authors*:      [Michael Hucka](http://github.com/mhucka)<br>
*Repository*:   [https://github.com/caltechlibrary/martian](https://github.com/caltechlibrary/martian)<br>
*License*:      BSD/MIT derivative &ndash; see the [LICENSE](LICENSE) file for more information

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg?style=flat-square)](https://choosealicense.com/licenses/bsd-3-clause)
[![Python](https://img.shields.io/badge/Python-3.4+-brightgreen.svg?style=flat-square)](http://shields.io)
[![Latest release](https://img.shields.io/badge/Latest_release-1.0.0-b44e88.svg?style=flat-square)](http://shields.io)


Table of Contents
-----------------
* [Introduction](#-introduction)
* [Installation instructions](#-installation-instructions)
* [Basic operation](#︎-basic-operation)
* [Getting help and support](#-getting-help-and-support)
* [Do you like it?](#-do-you-like-it)
* [Acknowledgments](#︎-acknowledgments)
* [Copyright and license](#︎-copyright-and-license)


☀ Introduction
-----------------------------

Caltech's librarians occasionally need to download large numbers of records from Caltech's TIND.io database.  Doing this through TIND's web interface is tedious.  _Martian_ is a program to make this work easier.  It does a simple task: run a query in caltech.tind.io and download all the results in MARC XML format to a file on the local computer.


✺ Installation instructions
---------------------------

The developers provide an installer program for Caltech Library users.  Please contact the developers to get a copy of the installer program for Windows 7, Windows 10, or macOS 10.12+.  Note also that installation of _Martian_ on Windows requires administrator priviledges.

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

▶︎ Basic operation
------------------



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
