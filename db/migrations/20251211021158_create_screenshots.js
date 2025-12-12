/**
 * @param { import("knex").Knex } knex
 * @returns { Promise<void> }
 */
exports.up = function(knex) {
  return knex.schema.createTable('screenshots', (table) => {
    table.bigIncrements('id').primary();
    table.bigInteger('computer_id')
         .notNullable()
         .references('id')
         .inTable('computers')
         .onDelete('CASCADE');
    table.text('image_base64');                    // we'll store latest few
    table.timestamp('captured_at').defaultTo(knex.fn.now());

    table.index('computer_id');
    table.index('captured_at');
  });
};

/**
 * @param { import("knex").Knex } knex
 * @returns { Promise<void> }
 */

exports.down = function(knex) {
  return knex.schema.dropTable('screenshots');
};