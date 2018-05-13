'use strict'

/**
 * Dependencies
 * @ignore
 */
const Constants = require('./Constants')

/**
 * Constants
 * @ignore
 */
const {
  draw,
  roomSize
} = Constants

/**
 * Point
 * @ignore
 */
class Point {
  constructor (room, x, y, v) {
    Object.defineProperty(this, 'room', { value: room })
    Object.defineProperty(this, 'x', { value: x, enumerable: true })
    Object.defineProperty(this, 'y', { value: y, enumerable: true })
    Object.defineProperty(this, 'v', { value: v, enumerable: true })
  }

  static get border () {
    if (!this._border) {
      this._border = new Point()
    }

    return this._border
  }

  getNeighbourhood () {
    const MoorNeighbourhood = require('./MoorNeighbourhood')
    return MoorNeighbourhood.getNeighbourhood(this)
  }

  get edge () {
    return this.x === 0 || this.x === roomSize - 1
      || this.y === 0 || this.y === roomSize - 1
  }

  get border () {
    return this.v === draw.border
  }

  get clear () {
    return this.v === draw.clear
  }

  get wall () {
    return this.v === draw.wall
  }

  get swamp () {
    return this.v === draw.swamp
  }

  get both () {
    return this.v === draw.both
  }

  isDrawn (type) {
    return this.both || this.v === type
  }
}

/**
 * Exports
 * @ignore
 */
module.exports = Point
