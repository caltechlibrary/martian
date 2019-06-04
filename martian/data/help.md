<h1 align="center">Help for Martian</h1>

Basic operation
---------------

_Martian_ has both a GUI interface and a command-line interface.  The GUI interface is simple: a user starts the program in a typical way (e.g., by double-clicking the program icon) and _Martian_ creates a main window, then immediately begins its work by connecting to Caltech.tind.io and asking the user for information.

After the user types in a search query string and indicates where the output should be written, and clicks the **OK** button, the program does the following behind the scenes:

1. Searches Caltech.tind.io with the query string
2. Downloads the data returned by TIND in a loop until there is no more data
3. Writes the output file
