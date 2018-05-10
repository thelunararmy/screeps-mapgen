'''
Created on May 10, 2018

@author: thelunararmy
'''
import json
from enum import Enum
from pyx import *

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
    return [map(int,row) for row in rows]
    

if __name__ == '__main__':
    # Fetch the data
    data = ConvertJsonMapToArrays('data/testdata01.json', True)
    
    # Categorize the rows into blobs
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
            
    '''      
        rect1 = path.path(  path.moveto(4,0),
                            path.lineto(5,0),
                            path.lineto(5,1),
                            path.lineto(4,1),
                            path.closepath()
                         )
        c.stroke(rect1, [style.linewidth.THICK])'''
    
    # Write to SVG file
    c.writeSVGfile('output/testy')
    print ('Done')