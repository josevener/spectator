// models/Computer.js
const { Model } = require('objection');

class Computer extends Model {
  static get tableName() {
    return 'computers';
  }

  static get idColumn() {
    return 'id';
  }

  static get relationMappings() {
    const Client = require('./Client');
    const Screenshot = require('./Screenshot');
    const Activity = require('./Activity');

    return {
      client: {
        relation: Model.BelongsToOneRelation,
        modelClass: Client,
        join: {
          from: 'computers.client_id',
          to: 'clients.id'
        }
      },
      screenshots: {
        relation: Model.HasManyRelation,
        modelClass: Screenshot,
        join: {
          from: 'computers.id',
          to: 'screenshots.computer_id'
        }
      },
      activities: {
        relation: Model.HasManyRelation,
        modelClass: Activity,
        join: {
          from: 'computers.id',
          to: 'activities.computer_id'
        }
      }
    };
  }
}

module.exports = Computer;