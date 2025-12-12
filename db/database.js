// src/db.js
require('dotenv').config();
const knex = require('knex');
const { Model } = require('objection');
const config = require('../knexfile');

const env = process.env.NODE_ENV || 'development';
const knexInstance = knex(config[env]);
Model.knex(knexInstance);

module.exports = knexInstance;