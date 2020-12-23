import urllib.request, json 
import random
from enum import Enum
import copy

class MAP():
    Layers = "layers"
    Width = "width"
    Height = "height"
    Tilesets = "tilesets"

class CONTENT():
    tileid = "tileid"
    title = "title"
    url ="url"
    x = "x"
    y = "y"

class LAYER():
    name = "name"
    data = "data"
    properties = "properties"

class LAYER_PROPERTY():
    name = "name"
    Type ="type"
    value = "value"
class LayerTypes(Enum):
    TILELAYER=0
    OBJECTGROUP=1

class Layer():
    layerid = 0
    @staticmethod
    def getNextLayerId():
        Layer.layerid=Layer.layerid+1
        return Layer.layerid

    @staticmethod
    def getLayerListPosByName(layerList,name):
        for pos,element in enumerate(layerList):
            if element.name == name:
                return pos

    def __init__(self,type: LayerTypes, width, height,name):
        if type == LayerTypes.TILELAYER:
            self.data = [0] * (width * height)
            self.type = "tilelayer"
            self.properties =  []
        if type == LayerTypes.OBJECTGROUP:
            self.objects = []
            self.type = "objectgroup"
        self.height = height 
        self.id = Layer.getNextLayerId() 
        self.name = name
        self.opacity = 1
        self.visible = True
        self.width  = width
        self.x = 0 # tiled doku says this is always zero
        self.y = 0 # tiled doku says this is always zero

class LayerProperty():
    
    def __init__(self,name,ptype,value):
        self.name = name
        self.type = ptype
        self.value = value



class Position():
    def __init__ (self,x,y):
        self.x = x
        self.y = y

    def isValid(self):
        if self.x >= 0 and self.y >=0:
            return True
        return False

    @staticmethod
    def toDataIndex(position, roomWidth):
        return (position.y*roomWidth)+position.x
    @staticmethod
    def toPosition(dataIndex, roomWidth):
        y = dataIndex // roomWidth
        x = dataIndex - (roomWidth * y)
        return Position(x,y)




class TILESET:
    firstgid = "firstgid"
    tilecount = "tilecount"
    tiles = "tiles"
    name="name"

class TILE:
    id = "id"
    properties = "properties"

class TILE_PROPERTY:
    name = "name"
    Type ="type"
    value = "value"

class Location():
    def __init__(self,positionInDataArray,validPlacementPosiotions):
        self.positionInDataArray = positionInDataArray
        self.validPlacementPosiotions = validPlacementPosiotions

class GeneratedMap():
    def __init__(self,data,filename):
        self.data = copy.deepcopy(data)
        self.filename = copy.deepcopy(filename)

class ProcessingMap():
    def __init__(self,mapDataTemplate,outputFileName,layerWithBooksName,tilesOfBookShelves,maxBooksOnMap,randomSeed):
        self.randomSeed = randomSeed
        self.layerWithBooksName = layerWithBooksName
        self.tilesOfBookShelves = tilesOfBookShelves
        self.maxBooksOnMap = maxBooksOnMap
        self.outputFileNameTemplate = outputFileName
        self.processedMaps = 0
        self.locationsUsed =[]
        self.height =  mapDataTemplate[MAP.Layers][0][MAP.Height]
        self.width =  mapDataTemplate[MAP.Layers][0][MAP.Width]
        self.mapDataTemplate = mapDataTemplate
        self.isSaved = False
        self.generatedMaps =[]
        self.initNewMap()
   
    def initNewMap(self):
        #init random
        self.isSaved = False
        random.seed(self.randomSeed) #TODO reinitalize on map change
        self.randomSeed = self.randomSeed+1

        self.processedMaps = self.processedMaps+1
        if hasattr(self, 'data'):
            self.generatedMaps.append(GeneratedMap(self.data,self.outputFileName))
            self.data.clear()

        self.data = copy.deepcopy(self.mapDataTemplate)
        self.possibleBookLocations = self.getPossibleLocations()
        self.locationsUsed.clear() 
        self.outputFileName =  self.outputFileNameTemplate.replace("#",str(self.processedMaps)) # generate the new filename for the output map
        print("ProcessingMap: init new map #"+str(self.processedMaps)+ " with filename "+self.outputFileName)

   
    def isTileColliding(self,tileId):
        # find the tileset responsible for the tileid
        for tileset in self.data[MAP.Tilesets]:
            if tileId in range(tileset[TILESET.firstgid],tileset[TILESET.firstgid]+tileset[TILESET.tilecount]):
                # we found the tileset our tileid belongs to
                # now calc the tileid in the tileset
                innerTileId = tileId - (tileset[TILESET.firstgid]-1)
                for tile in tileset[TILESET.tiles]:
                    if tile[TILE.id]== innerTileId:
                        #we found a tile description
                        for tileProperty in tile[TILE.properties]:
                            if (tileProperty[TILE_PROPERTY.name] == "collides") and (tileProperty[TILE_PROPERTY.value]== True):
                                #tile is colliding
                                return True
                return False
        return False #just to be shure...    

 
    #checks if one of the surrounding fields is accessable for a avatar
    def checkNeighbourhood(self,layer,dataPos):
        position = Position.toPosition(dataPos,self.width)
        tmap = [[0,1],[0,-1],[1,0],[-1,0]]
        valids = []
        for xy in tmap:
            newPosition= Position(position.x+xy[0],position.y+xy[1])

            if newPosition.isValid():
                posD = Position.toDataIndex(newPosition,self.width)
                if len(layer[LAYER.data]) > posD:
                    tile = layer[LAYER.data][posD]-1
                    if not self.isTileColliding(tile): #TODO check for collisions with other links!
                        #Found accessable tile in neghbourhood
                        valids.append(posD)

        return valids        

    def getPossibleLocations(self):
        # find corresponding layer
        possibleLocation = []
        for layer in self.data[MAP.Layers]:
            if layer[LAYER.name] == self.layerWithBooksName:
                layerWithBooks = layer
                break
        #go trough all bookshelf tiles
        for dataPos in range(len(layerWithBooks[LAYER.data])):
            tileidOnLayer = layerWithBooks[LAYER.data][dataPos]
            if tileidOnLayer in self.tilesOfBookShelves:
                valids = self.checkNeighbourhood(layerWithBooks,dataPos)
                if len(valids) > 0:
                    possibleLocation.append(Location(dataPos,valids))
        return possibleLocation

    def getTileID(self,tileset_name, tileId):
        for tileset in self.data[MAP.Tilesets]:
            if (tileset[TILESET.name]== tileset_name):
                newTileId = tileset[TILESET.firstgid]+tileId
                return newTileId
        raise NameError("cannot find tileset "+tileset_name+" in template")

    def giveRandomizedLocation(self):
        locationNotFound = True
        while locationNotFound:
            locationIndex = random.randint(0,len(self.possibleBookLocations)-1)
            if not locationIndex in self.locationsUsed:
                break
            #TODO abort if no location can be found
        newLocation = self.possibleBookLocations[locationIndex]
        self.locationsUsed.append(newLocation)
        return newLocation

    def setLayerProperty(self, data,layerName,propertyName, value):
        for layer in data[MAP.Layers]:
            if layer[LAYER.name] == layerName:
                for prop in layer[LAYER.properties]:
                    if prop[LAYER_PROPERTY.name] == propertyName:
                        prop[LAYER_PROPERTY.value] = value
                        break
                break
                

    def postprocess(self):
        if len(self.locationsUsed)>0:
            self.generatedMaps.append(GeneratedMap(self.data,self.outputFileName))
            print("ProcessingMap: postprocess: added "+self.outputFileName)
        # remove last stairway to heaven :-)
        lastMap = self.generatedMaps[-1]
        for layer in lastMap.data[MAP.Layers]:
            if layer[LAYER.name]=="toNext":
                lastMap.data[MAP.Layers].remove(layer)
                break
        
        #set links between floors
        for index in range (1,len(self.generatedMaps)):
            previousGenMap = self.generatedMaps[index-1]
            actualGenMap = self.generatedMaps[index]
            self.setLayerProperty(previousGenMap.data,"toNext","exitSceneUrl",actualGenMap.filename+"#fromBottom")
            self.setLayerProperty(actualGenMap.data,"toPrev","exitSceneUrl",previousGenMap.filename+"#fromTop")
            




    def saveMaps(self):
        for ele in self.generatedMaps:

            #save the map     
            mapOutput = json.dumps(ele.data, default=lambda o: o.__dict__, 
                sort_keys=True, indent=2)
            with open(ele.filename,'w+') as roomjsonfile:
                roomjsonfile.write(mapOutput)
            print("ProcessingMap: saved file "+ele.filename)

 

    def checkIfNewMapIsNeeded(self):
        #TODO check if there are possible locations left
        if len(self.locationsUsed) >= self.maxBooksOnMap:
            #we reached books limit
            self.initNewMap()


def main():
    #constants, (TODO grab them from args?)
    MAX_BOOKS_ON_FLOOR = 5 #TODO check if number is useable, adapt if needed
    FILENAME_MAP_TEMPLATE ="bib-og.json"
    FILENAME_MAP_OUTPUT="bib-og_#.json"
    FILENAME_CONTENT_DEFINTION = "contentDefinition.json"
    FILENAME_CONTENT_DEFINITION_OUTPUT = "contentDefinitionWithPos.json"
    RANDOM_SEED = 2342001 #seed to make the "random" numbers predictable
    TILE_ID_FLOOR = 23
    TILESET_NAME_CONTAINING_BOOKS_FOR_CONTENT = "books"
    LAYER_NAME_BOOKS = "Floor"
    TILES_OF_BOOKSHELVES = [48,49,50,51,52,53,54,
                            64,65,66,67,68,69,70,
                            80,81,82,83,
                            96,97,98,99,
                            112,113,114,115,
                            128,129,130,131,
                            144,145,146,147,
                            160,161,162,163,
                            167,168,169,170]
                    
    
    # load base map
    with open(FILENAME_MAP_TEMPLATE) as map_file:
        mapTemplateData = json.load(map_file)


    #load content definition 
    with open(FILENAME_CONTENT_DEFINTION) as json_file:
        content_definiton = json.load(json_file)

    #main loop

    currentMap = ProcessingMap(mapTemplateData,FILENAME_MAP_OUTPUT, LAYER_NAME_BOOKS,TILES_OF_BOOKSHELVES,MAX_BOOKS_ON_FLOOR,RANDOM_SEED)

    #we have to place every content
    for content in content_definiton:

        #get next randomized possible location on map. This includes position of the book tile and position of valid link tiles
        newLocation = currentMap.giveRandomizedLocation()

        
        #new layer, because the layer has the link info
        newLayer = Layer(LayerTypes.TILELAYER,currentMap.width,currentMap.height,content[CONTENT.title])
        newLayer.properties.append(LayerProperty("openWebsite", "string", content[CONTENT.url])) 

        #set a tile on the position to show the book
        tileId = currentMap.getTileID(TILESET_NAME_CONTAINING_BOOKS_FOR_CONTENT,content[CONTENT.tileid])
        newLayer.data[newLocation.positionInDataArray] = tileId

        #add floortiles for accessing the link
        for newFloorTilePosD in newLocation.validPlacementPosiotions:
            newLayer.data[newFloorTilePosD] = TILE_ID_FLOOR+1

        #add the layer to the map
        currentMap.data[MAP.Layers].insert(len(currentMap.data[MAP.Layers])-1,newLayer)


        position = Position.toPosition(newLocation.positionInDataArray,currentMap.width)
        print ("processing " + content[CONTENT.title]+" on data="+str(newLocation.positionInDataArray)+" pos x="+str(position.x)+" y:"+str(position.y))
        content["x"] = position.x
        content["y"] = position.y
        content["file"] = currentMap.outputFileName
        
        currentMap.checkIfNewMapIsNeeded()
    currentMap.postprocess()
    currentMap.saveMaps() #save the last processed map in case that book limit was not reached in loop

   #save the content definition with position information
    contentOutput = json.dumps(content_definiton, default=lambda o: o.__dict__, 
            sort_keys=True, indent=2)
    with open(FILENAME_CONTENT_DEFINITION_OUTPUT,'w+') as contentoutputjsonfile:
        contentoutputjsonfile.write(contentOutput)






if __name__ == "__main__":
    main()