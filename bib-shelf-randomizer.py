#!/usr/bin/env python3

import sys
import json
import random


def main():
    filename = sys.argv[1]
    rnd_groups = [
        [48,49,50,51,52,53,54],
        [64,65,66,67,68,69,70],
        [80,96,112,128,144,160,176],
        [81,97,113,129,145,161,177],
        [82,98,114,130,146,162,178],
        [83,99,115,131,147,163,179]
    ]
    # Read data
    with open(filename) as json_file:
        map = json.load(json_file)
    # Find Floor layer
    for layer in map['layers']:
        if layer['name'] == 'Floor':
            # Parse data
            for n in range(0, len(layer['data'])):
                for g in rnd_groups:
                    # If tile is rnd_group...
                    if layer['data'][n] in g:
                        # Replace with random selection
                        new_value = g[random.randrange(len(g))]
                        # print('Replacing %d with %d' % ( layer['data'][n], new_value))
                        layer['data'][n] = new_value
    # Write JSON
    with open(filename, 'w') as outfile:
        json.dump(map, outfile)


if __name__ == "__main__":
    main()