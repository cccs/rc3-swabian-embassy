#!/bin/bash

if [[ ! -f ds-links.txt ]] ; then
  curl https://ds.ccc.de/download.html | xmlstarlet fo | sed "s/href/#/g" | tr "#" "\n"  | grep "ds.ccc.de/pdfs/" | sed "s/^.*https/https/;s/\".*$//" | sort -u > ds-links.txt
fi
cat ds-links.txt | while read LINE ; do
  NR=`echo $LINE | sed "s/^.*ds//;s/\.pdf.*$//"`
  if [[ ${#NR} -eq 4 ]] ; then
    NR=${NR:0:2}/${NR:2:2}
  fi
  NR=`echo $NR | sed "s/^0*//;s/\/0*/\//"`
  echo "{ \"title\": \"Datenschleuder $NR\", \"url\": \"$LINE\", \"tileid\": $(( $RANDOM % 4 )) },"
done

