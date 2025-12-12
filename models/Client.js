// models/Client.js
const { Model } = require('objection');

class Client extends Model {
  static get tableName() {
    return 'clients';
  }

  static get idColumn() {
    return 'id';
  }
}

module.exports = Client;