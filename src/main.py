'''
Created on May 10, 2018

@author: thelunararmy
'''
import json
from enum import Enum
from pyx import *
from queue import *
from gettext import find

# Ebnumerator for tile types
class Tile(Enum):
    BLANK = 0
    WALL = 1
    SWAMP = 2
    UNKOWN = 3

# Map tile type to color
TileToColor = {
    Tile.BLANK  :   color.rgb.white,
    Tile.WALL   :   color.rgb.black,
    Tile.SWAMP  :   color.rgb.green,
    Tile.UNKOWN :   color.rgb.blue
}

def ConvertJsonMapToArrays (jsonfilename,debug = False):
    ''' Converts json file from Screeps into 50x50 rows to be manipulated '''
    # load json file and extract data
    with open (jsonfilename) as file:
        data = json.load(file)
    
    # Fetch rows in 50 character increments
    if debug: print (data['terrain'],'\n')
    d = data['terrain']
    rows = [data['terrain'][x*50:(x+1)*50] for x in range(0,50)]
    if debug: 
        for row in rows: print (row)
    if debug: print (len(rows))
    
    # Return data
    return [[int(x) for x in row] for row in rows]

def BasicMapGenerator(data):
    c = canvas.canvas()
    rowblobs = []
    for row in data:
        blobs = []
        previousItem = -1
        runningBlob = 0
        for item in row:
            # Inspect item
            if (previousItem == -1): # Skip starting item
                runningBlob = 1
                previousItem = item
            elif item == previousItem: # The current item is the same as the previous item
                runningBlob += 1
            else: # Different item, start new blob
                blobs.append((previousItem,runningBlob))
                runningBlob = 1
                previousItem = item
                
        # Add last running blob to blob
        blobs.append((previousItem,runningBlob))
        rowblobs.append(blobs)  
    
    # Draw Row blobs
    for rowPos,blobs in enumerate(rowblobs[::-1]):
        colPos = 0
        for (itemType,blobSize) in blobs:
            # Get the blob's color to draw
            itemColor = TileToColor[Tile(itemType)]
            
            # Determine blob type 
            if itemType == 0: # this is white space, so just ignore everything
                pass    
            elif itemType in [1,2,3]: # this is actual fill
                rect = path.path(
                    # Move to current colomn position within the row
                    path.moveto(colPos,rowPos),
                    # Create a box with three sides and then closed
                    path.lineto(colPos+blobSize,rowPos),
                    path.lineto(colPos+blobSize,rowPos+1),
                    path.lineto(colPos,rowPos+1),
                    path.closepath()
                )
                
                # Draw the box on the canvas
                c.stroke(rect, 
                         [
                             style.linewidth.THICK,
                             deco.filled([itemColor]),
                             itemColor
                        ])
            # At the end of the blob, move new pen x-pos origin to blob size
            colPos += blobSize  
    # Write svg 
    c.writeSVGfile('output/testy')

def FindNeighbours(data, width, height, start_x, start_y, pixelFlags):
    listOfNeighbours = []
    
    q = Queue()
    q.put_nowait((start_x,start_y))
    
    while not q.empty():
        (px,py) = q.get_nowait()
        tileType = Tile(data[px][py])
        for x in range(px-1,px+2):
            for y in range(py-1,py+2):
                if IsInMapRange(x, y, width, height) and (x == px or y == py) :
                    if Tile(data[x][y]) == tileType and not pixelFlags[x][y]:
                        pixelFlags[x][y] = 1
                        listOfNeighbours.append((x,y))
                        q.put_nowait((x,y))
                        
    return listOfNeighbours

def IsInMapRange(x,y,width,height):
    return not (x < 0 or x >= width or y < 0 or y >= height)

if __name__ == '__main__':
    # Fetch the data
    data = ConvertJsonMapToArrays('data/testdata01.json', True)

    #BasicMapGenerator(data)
    c = canvas.canvas()
    
    width = len(data[0])
    height = len(data)
    pixelFlags = [[0] * width for _ in range(height)]
    
    listy = FindNeighbours(data, width, height, 0, 0, pixelFlags)
    
    itemColor = TileToColor[Tile(1)]
    begin_x, begin_y = listy[0]
    
    '''
    for row in data:
        print ("".join(map(str,row)))
    '''
    
    outline = []
    rect = path.path()
    for (x,y) in listy: 
        rect.append(path.moveto(y,x))
                        # Move to current colomn position within the row
        rect.append(path.lineto(y+1,x))
        rect.append(path.lineto(y+1,x+1))
        rect.append(path.lineto(y,x+1))
        rect.append(path.closepath())                                

                    
    # Draw the box on the canvas
    c.stroke(rect, 
             [
                 style.linewidth.THICK,
                 #deco.filled([itemColor]),
                 itemColor
            ])
    cc = canvas.canvas()
    cc.insert(c,[trafo.mirror()])
    cc.writeSVGfile('output/testy')
    
    
    print ('Done')