'use strict'

/**
 * Dependencies
 * @ignore
 */
const Point = require('./Point')
const Constants = require('./Constants')

/**
 * Constants
 * @ignore
 */
const {
  roomSize,
} = Constants

/**
 * MoorNeighbourhood
 * @ignore
 */
class MoorNeighbourhood {
  constructor (points) {
    Object.defineProperty(this, 'points', { value: points })
    Object.defineProperty(this, 'values', {
      value: this.points.map(point => point ? point.v : undefined),
      enumerable: true
    })
  }

  static getNeighbourhood(point) {
    const { x, y, room } = point

    const topEdge = y === 0
    const leftEdge = x === 0
    const bottomEdge = y === roomSize - 1
    const rightEdge = x === roomSize - 1

    return new MoorNeighbourhood([
      topEdge || leftEdge ? Point.border : room.getCoord(x-1, y-1),
      topEdge ? Point.border : room.getCoord(x, y-1),
      topEdge || rightEdge ? Point.border : room.getCoord(x+1, y-1),
      leftEdge ? Point.border : room.getCoord(x-1, y),
      point,
      rightEdge ? Point.border : room.getCoord(x+1, y),
      bottomEdge || leftEdge ? Point.border : room.getCoord(x-1, y+1),
      bottomEdge ? Point.border : room.getCoord(x, y+1),
      bottomEdge || rightEdge ? Point.border : room.getCoord(x+1, y+1),
    ])
  }

  get pTopLeft () {
    return this.points[0]
  }

  get pTop () {
    return this.points[1]
  }

  get pTopRight () {
    return this.points[2]
  }

  get pLeft () {
    return this.points[3]
  }

  get pMiddle () {
    return this.points[4]
  }

  get pRight () {
    return this.points[5]
  }

  get pBottomLeft () {
    return this.points[6]
  }

  get pBottom () {
    return this.points[7]
  }

  get pBottomRight () {
    return this.points[8]
  }
}

/**
 * Exports
 * @ignore
 */
module.exports = MoorNeighbourhood
