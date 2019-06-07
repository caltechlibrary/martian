#!/bin/bash
# This script was provided by Kathy McCarthy <support@tind.io> to
# Laurel Narizny via email on 2019-05-11.  Here's the context in the
# original email:
#
#  "You're 100% correct that the download managers are only giving you 200
#  records because that's the unauthenticated limit within TIND and these
#  other tools can't manage that. There will be some improvements made to
#  this area of the system in the future but in the meantime, we thought it
#  might be helpful to provide you with a pagination script that should allow
#  you to export large sets of records within the opac without the browser
#  timing out.

EXPORTURL="https://caltech.tind.io/search?ln=en&p=norway&of=xm"

RESULTS_PER_PAGE=200
JREC=1
CONTENT="<collection>"
echo "$CONTENT" > test.xml
while [[ ! -z $CONTENT ]]
do
CONTENT=$(curl "$EXPORTURL&rg=$RESULTS_PER_PAGE&jrec=$JREC" | grep -vE "<?collection.*>" | grep -v "<?xml version="1.0" encoding="UTF‌-8"?>")
echo "$CONTENT" >> test.xml
JREC=$(($JREC+$RESULTS_PER_PAGE))
done
echo "</collection>" >> test.xml
