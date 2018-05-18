'''
Testing out some random map generator functions

Created on May 17, 2018

@author: thelunararmy
'''

from sys import float_info

global Permutation, P, Repeat
Permutation = [151,160,137,91,90,15,                    
        131,13,201,95,96,53,194,233,7,225,140,36,103,30,69,142,8,99,37,240,21,10,23,    
        190, 6,148,247,120,234,75,0,26,197,62,94,252,219,203,117,35,11,32,57,177,33,
        88,237,149,56,87,174,20,125,136,171,168, 68,175,74,165,71,134,139,48,27,166,
        77,146,158,231,83,111,229,122,60,211,133,230,220,105,92,41,55,46,245,40,244,
        102,143,54, 65,25,63,161, 1,216,80,73,209,76,132,187,208, 89,18,169,200,196,
        135,130,116,188,159,86,164,100,109,198,173,186, 3,64,52,217,226,250,124,123,
        5,202,38,147,118,126,255,82,85,212,207,206,59,227,47,16,58,17,182,189,28,42,
        223,183,170,213,119,248,152, 2,44,154,163, 70,221,153,101,155,167, 43,172,9,
        129,22,39,253, 19,98,108,110,79,113,224,232,178,185, 112,104,218,246,97,228,
        251,34,242,193,238,210,144,12,191,179,162,241, 81,51,145,235,249,14,239,107,
        49,192,214, 31,181,199,106,157,184, 84,204,176,115,121,50,45,127, 4,150,254,
        138,236,205,93,222,114,67,29,24,72,243,141,128,195,78,66,215,61,156,180]
    
P = [Permutation[x % 256] for x in range(0,512)]

Repeat = -1

def Lerp (a,b,x):
    return ( a + x * (b - a))

def InverseLerp (a,b,x):
    return (x - a) / (b - a)

def Fade (t):
    return t * t * t * ( t * ( t * 6 - 15 ) + 10 )


def Grad(hash, x, y, z):
    h = hash & 0b1111
    u = x if h < 0b1000 else y
    if (h < 0b0100):
        v = y
    elif (h == 0b1100 or h == 0b1110):
        v = x 
    else:
        v = z
    return (u if (h & 0b1) == 0 else -u) + (v if (h & 0b10) == 0 else -v)


def Inc(num):
    num = num + 1
    if (Repeat > 0): num = num % Repeat 
    return num



def Perlin (x, y, z):    
    if (Repeat > 0):
        x = x % Repeat
        y = y % Repeat
        z = z % Repeat
    
    xi = int(x) & 0xff
    yi = int(y) & 0xff
    zi = int(z) & 0xff
    xf = x - int(x)
    yf = y - int(y)
    zf = z - int(z)
    u = Fade(xf)
    v = Fade(yf)
    w = Fade(zf)
    
    aaa = P[P[P[    xi ]+    yi ]+    zi ];
    aba = P[P[P[    xi ]+Inc(yi)]+    zi ];
    aab = P[P[P[    xi ]+    yi ]+Inc(zi)];
    abb = P[P[P[    xi ]+Inc(yi)]+Inc(zi)];
    baa = P[P[P[Inc(xi)]+    yi ]+    zi ];
    bba = P[P[P[Inc(xi)]+Inc(yi)]+    zi ];
    bab = P[P[P[Inc(xi)]+    yi ]+Inc(zi)];
    bbb = P[P[P[Inc(xi)]+Inc(yi)]+Inc(zi)];
    
    #print ("xi", xi, "yi", yi, "zi", zi, "u", u, "v", v, "w", w)
    
    x1 = Lerp ( Grad( aaa, xf, yf, zf ),    Grad (baa, xf-1,yf,  zf),  u )
    x2 = Lerp ( Grad( aba, xf, yf-1, zf ),  Grad (bba, xf-1,yf-1,zf),  u )
    y1 = Lerp ( x1, x2, v )
    
    x1 = Lerp ( Grad( aab, xf, yf, zf-1 ),  Grad (bab, xf-1, yf, zf-1), u )
    x2 = Lerp ( Grad( abb, xf, yf-1, zf-1 ),Grad (bbb, xf-1,yf-1,zf-1), u )
    y2 = Lerp ( x1, x2, v )
    
    return (Lerp(y1,y2,w) + 1) * 0.5

def OctavePerlin(x, y, z, octaves, persistence):
    total = 0
    frequency = 1
    amplitude = 1
    maxValue = 0
    
    octaves = 0 if octaves < 0 else octaves
    
    for i in range(0, octaves):
        total += Perlin(x * frequency, y * frequency, z * frequency) * amplitude
        maxValue += amplitude
        amplitude *= persistence
        frequency *= 2
    
    return total/maxValue
    
    

class PerlinMapGen():
    def __init__(self,x,y,scale):
        self.x = 1 if x < 0 else x
        self.y = 1 if y < 0 else y
        self.scale = 0.1 if scale < 0 else scale
        # Generate our Perlinmap
        self.map = []
        
        maxValue = float_info.min
        minValue = float_info.max
        
        for y in range(0,self.y):
            row = []
            for x in range (0,self.x):
                pvalue = OctavePerlin(x*self.scale, y*self.scale, 0, 10, .5 )
                row.append(pvalue)
                maxValue = pvalue if pvalue > maxValue else maxValue
                minValue = pvalue if pvalue < minValue else minValue
            self.map.append(row)
        
        for y in range(0,self.y):
            for x in range (0,self.x):
                self.map[y][x] = InverseLerp(minValue, maxValue, self.map[y][x])
                
        
        
    
