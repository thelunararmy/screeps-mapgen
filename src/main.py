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

BlockSize = 100
hBlockSize = BlockSize / 2
global width, height, data

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

def TopMid (x,y):
    return x + hBlockSize, y
def LeftMid (x,y):
    return x, y + hBlockSize
def BotMid (x,y):
    return x + hBlockSize, y + BlockSize
def RightMid (x,y):
    return x + BlockSize, y + hBlockSize

def NV (pos,x,y):
    ''' Determines the value of the neighbourhood pixel '''
    '''     012
            3♥5
            678 where ♥ = position of our pixel ''' 
    tileType = Tile(data[x][y])
    relX = 0
    relY = 0
    if (pos == 0):
        relY = -1
        relX = -1
    elif(pos == 1):
        relX = -1
    elif(pos == 2):
        relY = 1
        relX = -1
    elif(pos == 3):
        relY = -1
    elif(pos == 5):
        relY = 1
    elif(pos == 6):
        relY = -1
        relX = 1
    elif(pos == 7):
        relX = 1
    elif(pos == 8):
        relY = 1
        relX = 1
    deltaX = x + relX
    deltaY = y + relY
    if deltaX < 0 or deltaX >= width or deltaY < 0 or deltaY >= height:
        return tileType == Tile.WALL
    else:
        return tileType == Tile(data[deltaX][deltaY])
    
    

def IsInMapRange(x,y):
    return not (x < 0 or x >= width or y < 0 or y >= height)

if __name__ == '__main__':
    # Fetch the data
    data = ConvertJsonMapToArrays('data/testdata01.json', False)

    #BasicMapGenerator(data)
    c = canvas.canvas()
    
    data = [[1,0,0,0],[1,1,0,0],[0,1,0,0],[0,1,0,0]]
    
    width = len(data[0])
    height = len(data)
    
    pixelFlags = [[0] * width for _ in range(height)]
    
    for x in range(1,2): # width col 
        for y in range(1,2): # height row
            # determine pixel type
            tileType = Tile(data[x][y])
            # skip if this pixel has already been drawn or blank space
            if pixelFlags[x][y] or tileType == Tile.BLANK: continue
            # set flag as draw
           
            # create new path to draw
            p = path.path()
            # get actual x,y
            dx = x * BlockSize
            dy = y * BlockSize
            
            # move to tmid
            p.append(path.moveto_pt(*TopMid(dx,dy)))
            # Determine shape of top left corner
            if NV(3,x,y):
                if (NV(0,x,y) and NV(1,x,y)) or (not NV(0,x,y) and not NV(1,x,y)): # Right Angle
                    p.append(path.lineto_pt(dx,dy))
                    p.append(path.lineto_pt(dx,dy+hBlockSize))
                elif(NV(0,x,y) and not NV(1,x,y)): # Cowlick
                    p.append(path.curveto_pt(*TopMid(dx,dy),dx,dy,dx,dy-hBlockSize))
                    p.append(path.lineto_pt(*LeftMid(dx, dy)))
            else:
                p.append(path.curveto_pt(*TopMid(dx,dy),dx,dy,(*LeftMid(dx,dy))))
            
            # Keep count of how far we progress
            yCount = 0
            # Determine if there is more blocks to goto
            if (NV(7,x,y) or not (y+1 >= height)):
                # Continue until we find an end
                for yc in range(y+1,height):
                    dyc = yc * BlockSize    
                    # Break if this block is not acceptable
                    if pixelFlags[x][yc] or tileType == Tile.BLANK: break
                    # Otherwise we good
                    pixelFlags[x][yc] = 1
                    yCount += 1 
                    
                    # Move pen to new origin
                    p.append(path.lineto_pt(dx, dyc))
                    
                    # Determine if we need to cowlick left or continue straight
                    print (x,yc)
                    if (NV(0,x,yc) and not NV(3,x,yc)):
                        p.append(path.lineto_pt(dx - hBlockSize, dyc))
                        p.append(path.curveto_pt(dx-hBlockSize,dyc,dx,dyc,(*LeftMid(dx,dyc))))
                    # Else just go straight
                    else:
                        p.append(path.lineto_pt(*LeftMid(dx,dyc)))
                
            # At the end of the block, draw bottom left corner
            # TODO continue here
                
                

                
                
                
            # Draw the path
            c.stroke(p, 
                 [
                     style.linewidth.THICK,
                     color.rgb.black
                ])
                    

                        
            
                
                
        

    cc = canvas.canvas()
    cc.insert(c,[trafo.mirror()])
    cc.writeSVGfile('output/testy')
    
    
    print ('Done')