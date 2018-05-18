'use strict'

/**
 * Dependencies
 * @ignore
 */
const crypto = require('crypto')
const noise = require('perlin-noise')

/**
 * PerlinGenerator
 * @ignore
 */
class PerlinGenerator {
  constructor (noise) {
    const min = Math.min(...noise)
    const max = Math.max(...noise)

    this.noise = noise.map(float => (float - min) / (max - min))
  }

  static generate (x, y, options = {}) {
    const noiseMap = noise.generatePerlinNoise(x, y, Object.assign({
      octaveCount: 4,
      amplitude: 0.1,
      persistence: 0.2,
    }, options))

    return new PerlinGenerator(noiseMap)
  }

  interpret (levels = [{ level: 0.5, value: 1 }]) {
    levels = levels.sort((a, b) => a < b ? -1 : a > b ? 1 : 0).reverse()
    return this.noise.map(float => (levels.find(item => float >= item.level) || {}).value || 0)
  }
}

/**
 * Exports
 * @ignore
 */
module.exports = PerlinGenerator
