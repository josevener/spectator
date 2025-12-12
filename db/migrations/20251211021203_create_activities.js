/**
 * @param { import("knex").Knex } knex
 * @returns { Promise<void> }
 */
exports.up = function(knex) {
  return knex.schema.createTable('activities', (table) => {
    table.bigIncrements('id').primary();
    table.bigInteger('computer_id')
         .notNullable()
         .references('id')
         .inTable('computers')
         .onDelete('CASCADE');
    table.float('cpu');        // 0-100
    table.float('ram');        // GB used
    table.bigInteger('uptime'); // seconds
    table.string('active_app', 300);
    table.timestamp('timestamp').defaultTo(knex.fn.now());

    table.index('computer_id');
    table.index('timestamp');
  });
};

/**
 * @param { import("knex").Knex } knex
 * @returns { Promise<void> }
 */

exports.down = function(knex) {
  return knex.schema.dropTable('activities');
};