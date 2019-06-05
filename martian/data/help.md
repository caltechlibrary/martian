<h1 align="center">Help for Martian</h1>

Installing and uninstalling Martian
-----------------------------------

The developers provide an installer program for Caltech Library users.  Note also that installation of _Martian_ on Windows requires administrator priviledges.

To uninstall _Martian_ on a Windows 10 system, use the normal Windows **Add or remove programs** facility in the **Systems Settings** panel.


Using Martian
-------------

_Martian_ has both a GUI interface and a command-line interface.  The GUI interface is simple: a user starts the program in a typical way (e.g., by double-clicking the program icon) and _Martian_ creates a main window, then immediately begins its work by connecting to caltech.tind.io and asking the user for information.

<center>
<img align="center" width="50%" src=".graphics/screenshot-first-screen-windows.png">
</center>

The first field ("Search (or URL)") can be either a search string as one would type into the caltech.tind.io search field, or alternatively, a complete search URL (e.g., copied from a web browser's address bar after performing some exploratory searches in caltech.tind.io).  The second field is used to specify where the output should be written.  The output file can be either typed in manually, or the "Browse" button can be used to choose a folder and file name.

After the user types in a search query string and indicates where the output should be written, and clicks the **OK** button, the program does the following behind the scenes:

1. Searches Caltech.tind.io with the query string
2. Downloads the data returned by TIND in a loop until there is no more data
3. Writes the output file

Martian prints messages about its progress as it runs.

Limitations
-----------

Because Martian gets data from TIND.io in batches of 200 at a time, interrupting Martian while it's running may result in either getting no data at all (if there is less than 200 to download) or getting up to 200 less than what it printed as its current progress point.

The GUI interface currently does not provide a way to indicate that Martian should get fewer than the maximum number of records returned by a given search, nor a way to indicate a starting record.  However, the command-line interface does provide options for setting these parameters at run time.

The choice of download format (which is MARC XML as produced by TIND.io), and the number of records it attempts to get per iteration (200) are currently fixed and hardwired into the program.
