#!/bin/bash
echo " *** SCRIPT TO GENERATE THE CSV FILE TO EXPORT IN *** "
 
echo -e "Environment (prod,test,dev)?"
read env
 
echo -e "Name of the csv file to be generated?"
read namefile
 
csvfile=$namefile
dom=ea.com
 
echo -e "Generating $csvfile file ....."
 
 
while IFS='' read -r line || [[ -n "$line" ]]; do
    exdomain=$(echo $line|awk -v FS='.' '{print $1}'); hpub=$exdomain.$dom
    exip=$(dig +short $hpub); intip=$(dig +short $line);
    echo -e "$line,$intip,$exip,$env" >> $csvfile
done < "$1"
 
echo "-- The file $csvfile has been generated --"
cat $csvfile
echo -e "*****************************************************************"
echo -e "*  Process $csvfile with the pasentryscv.py script                *"
echo -e "*   to add server entries in pas automatically --               *"           
echo -e "* ***        HOW  TO  USE  THE  SCRIPT ***                     *"
echo -e "*https://developer.ea.com/display/GOSInternal/Pas+Script+Howto  *"
echo -e "*-- Please verify the generated csv file info --                *"
echo -e "*                                                               *"
echo -e "*****************************************************************"

