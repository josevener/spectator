// models/Activity.js
const { Model } = require('objection');

class Activity extends Model {
  static get tableName() {
    return 'activities';
  }

  static get idColumn() {
    return 'id';
  }
}

module.exports = Activity;