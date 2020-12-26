#!/bin/bash
rm bib-og_*.json
./bibgen.py
for i in bib-og_*.json ; do
  ./bib-shelf-randomizer.py $i
done
