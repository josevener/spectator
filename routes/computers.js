// routes/computers.js
const express = require('express');
const router = express.Router();
const Computer = require('../models/Computer');
const Screenshot = require('../models/Screenshot');

router.get('/', async (req, res) => {
  const computers = await Computer.query().orderBy('display_name');
  res.json(computers);
});

router.get('/:id', async (req, res) => {
  const computer = await Computer.query().findById(req.params.id);
  if (!computer) return res.status(404).json({ error: 'Not found' });
  res.json(computer);
});

router.post('/', async (req, res) => {
  const { name, display_name } = req.body;
  if (!name || !display_name) return res.status(400).json({ error: 'Missing fields' });

  const secret_key = `sk_${name}_${Math.random().toString(36).substr(2, 9)}`;

  try {
    const computer = await Computer.query().insert({
      client_id: 1,
      name,
      display_name,
      secret_key,
    });
    res.status(201).json(computer);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

router.patch('/:id', async (req, res) => {
  const updates = req.body;
  try {
    const computer = await Computer.query().findById(req.params.id).patch(updates);
    if (!computer) return res.status(404).json({ error: 'Not found' });
    res.json({ success: true });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

router.delete('/:id', async (req, res) => {
  try {
    const deleted = await Computer.query().deleteById(req.params.id);
    if (!deleted) return res.status(404).json({ error: 'Not found' });
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.get('/:id/screenshot/latest', async (req, res) => {
  const screenshot = await Screenshot.query()
    .where('computer_id', req.params.id)
    .orderBy('captured_at', 'desc')
    .first();
  res.json(screenshot || { image_base64: null });
});

module.exports = router;