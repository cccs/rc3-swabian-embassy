# Swabian Embassy rC3 maps

## References / Credits

* tiles/floortileset.png: Chaosz0ne
* tiles/wood.png: rocketchat channel by @edloque
* tiles/furniture.png: cert tilesheet


### Script für die Stockwerkgenerierung
das bibgen.py script generiert durchnummerierte Stockwerke. Als Template wird das File bib-og.json angezogen.

Output sind dann durchnummerierte Stockwerksfiles nach dem Muster `bib-og_\<Stockwerksnummer\>`

Wie viele Stockwerke generiert werden hängt von der Anzahl der "Bücher" ab die in `contentDefinition.json` angegeben werden. Das Limit ab wann ein neues Stockwerk "eingezogen" wird ist hardcoded in bibgen.py festgelegt.