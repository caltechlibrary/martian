#!/bin/bash
# This is a simple example of using curl to get marc xml records from
# caltech.tind.io, to see what the output is like

# The fields in the request are like this:
#
# p    => the search string (here, "norway" is an example)
# of   => output format (here, "xml", for MARC XML)
# rg   => how many records to get
# jrec => starting record
#
# If you're going to loop, you'd keep increasing jrec by the rg amount.

curl "https://caltech.tind.io/search?ln=en&p=norway&of=xm&rg=5&jrec=1" > output.xml
