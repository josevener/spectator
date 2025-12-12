// models/Screenshot.js
const { Model } = require('objection');

class Screenshot extends Model {
  static get tableName() {
    return 'screenshots';
  }

  static get idColumn() {
    return 'id';
  }
}

module.exports = Screenshot;