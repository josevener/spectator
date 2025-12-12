// knexfile.js
require('dotenv').config();

const {
  DB_HOST = 'localhost',
  DB_PORT = 5432,
  DB_USER = 'postgres',
  DB_PASSWORD = '',
  DB_NAME = 'pc_monitor'
} = process.env;

module.exports = {
  development: {
    client: 'postgresql',
    connection: {
      host: DB_HOST,
      port: Number(DB_PORT),
      user: DB_USER,
      password: DB_PASSWORD,
      database: DB_NAME
    },
    migrations: { directory: './db/migrations' },
    seeds: { directory: './db/seeds' },
    pool: { min: 2, max: 10 }
  },

  production: {
    client: 'postgresql',
    connection: {
      host: DB_HOST,
      port: Number(DB_PORT),
      user: DB_USER,
      password: DB_PASSWORD,
      database: DB_NAME
    },
    migrations: { directory: './migrations' },
    pool: { min: 2, max: 20 }
  }
};