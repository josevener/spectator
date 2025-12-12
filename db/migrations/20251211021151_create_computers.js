/**
 * @param { import("knex").Knex } knex
 * @returns { Promise<void> }
 */
exports.up = function(knex) {
  return knex.schema.createTable('computers', (table) => {
    table.bigIncrements('id').primary();
    table.bigInteger('client_id')
         .notNullable()
         .references('id')
         .inTable('clients')
         .onDelete('CASCADE');

    table.string('name', 100).notNullable();
    table.string('display_name', 150).defaultTo('My Computer');
    table.string('secret_key', 200).notNullable();
    table.boolean('is_online').defaultTo(false);
    table.timestamp('last_seen');
    table.timestamp('created_at').defaultTo(knex.fn.now());

    table.unique(['client_id', 'name']);
    table.index('client_id');
    table.index('is_online');
    table.index('secret_key');
  });
};

/**
 * @param { import("knex").Knex } knex
 * @returns { Promise<void> }
 */

exports.down = function(knex) {
  return knex.schema.dropTable('computers');
};