'''
Created on May 10, 2018

@author: thelunararmy
'''
import json
from enum import Enum
from pyx import *

# Enumerator for tile types
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

# Output block sizes 
BlockSize = 50
hBlockSize = BlockSize / 2

# Globals for cross size
global width, height, data

def ConvertJsonMapToArrays (jsonfilename,debug = False):
    ''' Converts json file from Screeps into 50x50 rows to be manipulated '''
    # load json file and extract data
    with open (jsonfilename) as file:
        data = json.load(file)
    
    # Fetch rows in 50 character increments
    rows = [data['terrain'][x*50:(x+1)*50] for x in range(0,50)]
    if debug: 
        for row in rows: print (row)
    if debug: print (len(rows))
    
    # Return data
    return [[int(x) for x in row] for row in rows]

def BasicMapGenerator():
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
    for rowPos,blobs in enumerate(rowblobs):
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
    return c

def TopMid (x,y):
    return x + hBlockSize, y
def LeftMid (x,y):
    return x, y + hBlockSize
def BotMid (x,y):
    return x + hBlockSize, y + BlockSize
def RightMid (x,y):
    return x + BlockSize, y + hBlockSize

def NV (pos,y,x,debug = False):
    ''' Determines the value of the neighbourhood pixel '''
    '''     012
            3z5
            678 where z = position of our pixel ''' 
    tileType = Tile(data[y][x])
    relX = 0
    relY = 0
    if (pos == 0):
        relX = -1
        relY = -1
    elif(pos == 1):
        relY = -1
    elif(pos == 2):
        relX = 1
        relY = -1
    elif(pos == 3):
        relX = -1
    elif(pos == 5):
        relX = 1
    elif(pos == 6):
        relX = -1
        relY = 1
    elif(pos == 7):
        relY = 1
    elif(pos == 8):
        relX = 1
        relY = 1
    deltaX = x + relX 
    deltaY = y + relY
    
    if debug: print((y,x),(relY,relX),(deltaY,deltaX))
    
    if deltaX < 0 or deltaX >= height or deltaY < 0 or deltaY >= width:
        return tileType == Tile.BLANK
    else:
        if debug: print(Tile(data[deltaY][deltaX]),tileType == Tile(data[deltaY][deltaX]))
        return tileType == Tile(data[deltaY][deltaX])

def DrawCurvedMap():
    # Setup pixel registry
    pixelFlags = [[0] * width for _ in range(height)]
    
    # Iterate column by column
    for y in range(0,height): # width col 
        for x in range(0,width):
            # determine pixel type
            tileType = Tile(data[y][x])
            itemColor = TileToColor[tileType]
            
            # skip if this pixel has already been drawn or blank space
            if pixelFlags[y][x] or tileType == Tile.BLANK: continue

            # create new path to draw
            p = path.path()
            # get actual x,y
            dx = x * BlockSize
            dy = y * BlockSize

            # Move to start position
            p.append(path.moveto_pt(*TopMid(dx,dy)))       
                        
            # Top Left corner
            if NV(3,y,x):
                if (NV(0,y,x) and NV(1,y,x)) or (not NV(0,y,x) and not NV(1,y,x)): # Right Angle
                    p.append(path.lineto_pt(dx,dy))
                    p.append(path.lineto_pt(dx,dy+hBlockSize))
                elif(NV(0,y,x) and not NV(1,y,x)): # Cowlick
                    p.append(path.curveto_pt(*TopMid(dx,dy),dx,dy,dx,dy-hBlockSize))
                    p.append(path.lineto_pt(*LeftMid(dx, dy)))
            else:
                p.append(path.curveto_pt(*TopMid(dx,dy),dx,dy,(*LeftMid(dx,dy))))
            
            # Iterate through rest of column for continuous path
            yc = y    
            dyc = yc * BlockSize    
            while (NV(7,yc,x)) and (yc+1 < height):
                # Move to next block
                yc += 1 
                # Continue until we find an end
                dyc = yc * BlockSize             
                
                # Otherwise we good
                pixelFlags[yc][x] = 1
                
                # Move pen to new origin
                p.append(path.lineto_pt(dx, dyc))
                
                # Determine if we need to cowlick left or continue straight
                if (NV(0,yc,x) and not NV(3,yc,x)):
                    p.append(path.lineto_pt(dx - hBlockSize, dyc))
                    p.append(path.curveto_pt(dx-hBlockSize,dyc,dx,dyc,(*LeftMid(dx,dyc))))
                # Else just go straight
                else:
                    p.append(path.lineto_pt(*LeftMid(dx,dyc)))
                
            # Bottom left corner
            if NV(3,yc,x): # Right angle
                p.append(path.lineto_pt(dx, dyc + BlockSize))
                p.append(path.lineto_pt(*BotMid(dx, dyc)))
            else: # Round Curve
                p.append(path.curveto_pt(dx,dyc + hBlockSize,dx,dyc + BlockSize,(*BotMid(dx,dyc))))
            
            # Bottom right corner
            if NV(5,yc,x): # Right angle
                p.append(path.lineto_pt(dx + BlockSize, dyc + BlockSize))
                p.append(path.lineto_pt(*RightMid(dx, dyc)))
            else: # Round Curve
                p.append(path.curveto_pt(*BotMid(dx,dyc),dx + BlockSize ,dyc + BlockSize,(*RightMid(dx,dyc))))
    
    
            # Do lbit between BR and curve line going up
            # Determine if we need to cowlick right or continue straight
            if (NV(2,yc,x) and not NV(5,yc,x)):   
                p.append(path.curveto_pt(*RightMid(dx, dyc),dx + BlockSize, dyc,dx + BlockSize + hBlockSize, dyc))
                p.append(path.lineto_pt(dx + BlockSize, dyc))
            # Else just go straight
            else:
                p.append(path.lineto_pt(*RightMid(dx,dyc)))
    
    
            # Iterate up column for continuous path   
            while (NV(1,yc,x)and (yc-1 > 0)):
                # Move to next block
                yc -= 1 
                # Continue until we find an end
                dyc = yc * BlockSize    
                            
                # Move pen to new origin
                p.append(path.lineto_pt(*RightMid(dx, dyc)))
                
                # Determine if we need to cowlick right or continue straight
                if (NV(2,yc,x) and not NV(5,yc,x)):   
                    p.append(path.curveto_pt(*RightMid(dx, dyc),dx + BlockSize, dyc,dx + BlockSize + hBlockSize, dyc))
                    p.append(path.lineto_pt(dx + BlockSize, dyc))
                # Else just go straight
                else:
                    p.append(path.lineto_pt(*RightMid(dx,dyc)))
        
            # Top right corner
            if NV(5,y,x):
                if (NV(1,y,x) and NV(2,y,x)) or (not NV(1,y,x) and not NV(2,y,x)): # Right Angle
                    p.append(path.lineto_pt(dx + BlockSize,dy))
                    p.append(path.lineto_pt(*TopMid(dx, dy)))
                elif(not NV(1,y,x) and NV(2,y,x)): # Cowlick
                    p.append(path.lineto_pt(dx+BlockSize, dy-hBlockSize))
                    p.append(path.curveto_pt(dx+BlockSize, dy-hBlockSize,dx+ BlockSize,dy,*TopMid(dx,dy)))
            else:
                p.append(path.curveto_pt((*RightMid(dx,dy)),dx+BlockSize,dy,(*TopMid(dx,dy))))    
        
            # Close the completed path
            p.append(path.closepath())
                               
            # Draw the path
            c.stroke(p, 
                     [
                         style.linewidth.THICK,
                         deco.filled([itemColor]),
                         itemColor
                    ])                   

    return c

    

def IsInMapRange(x,y):
    return not (x < 0 or x >= width or y < 0 or y >= height)

if __name__ == '__main__':
    # Say hello then do work
    print ("Drawing map...")
        
    # Fetch the data
    data = ConvertJsonMapToArrays('data/testdata01.json', True)

    c = canvas.canvas()
    width = len(data[0])
    height = len(data)
    
    # Draw curved map
    c = DrawCurvedMap()
    # c = BasicMapGenerator() #just in case
    
    # Put it on new canvas to size and mirro'd correctly
    # TODO: get size correctly
    cc = canvas.canvas()
    cc.insert(c,[trafo.mirror()])
    cc.writeSVGfile('output/testy')
    
    
    print ('...Done')