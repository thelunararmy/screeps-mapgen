# Screeps SVG Map Generator _(screeps-mapgen)_

## CLI Usage

```
usage: screeps-mapgen [-h] [-v] [-g] [-s] [-b] [-t] data

Generate a SVG map from screeps terrian data

Positional arguments:
  data              Map data (JSON or raw) or path to input file

Optional arguments:
  -h, --help        Show this help message and exit.
  -v, --version     Show program's version number and exit.
  -g, --grid        Draw a grid over the map
  -s, --swamp       Draw swamp on the map
  -b, --background  Include background image under the map
  -t, --no-terrain  Disable drawing of terrain on the map
```

## Script Usage

```javascript
'use strict'

const Map = require('screeps-mapgen')
const roomData = require('.../rooms.terrain.json')

// Draw maps
const svgData = roomData.map(room => new Map(room.terrain).buildSVG(
  true, // Grid overlay
  true, // Draw swamp
  true, // Draw terrain
  true  // Include background
))

// Write maps (svgData) to different files
```
