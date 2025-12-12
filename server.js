// src/server.js — FINAL WORKING VERSION (SCREEN SHOWS INSTANTLY)
require('dotenv').config();
const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const cors = require('cors');
const morgan = require('morgan');

require('./db/database');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ 
  server,
  maxPayload: 500 * 1024 * 1024 // 50MB
});

app.use(cors({ origin: ['http://localhost:5300', 'http://10.0.2.51:5300'] }));
app.use(morgan('dev'));
app.use(express.json());

// Routes
const computerRoutes = require('./routes/computers');
app.use('/api/computers', computerRoutes);

app.get('/health', (req, res) => res.json({ status: 'ok' }));

// ──────────────────────────────────────────────────────────────
// CONNECTIONS
// ──────────────────────────────────────────────────────────────
const connections = {
  agents: new Map(),    // secret_key → { ws, computerId }
  viewers: new Map()    // computerId → Set<ws>
};

const Computer = require('./models/Computer');
const Screenshot = require('./models/Screenshot');
const Activity = require('./models/Activity');

function broadcast(computerId, data) {
  const viewers = connections.viewers.get(computerId);
  if (!viewers) return;
  const msg = JSON.stringify(data);
  viewers.forEach(ws => {
    if (ws.readyState === WebSocket.OPEN) ws.send(msg);
  });
}

// ──────────────────────────────────────────────────────────────
// ONLY ONE WEBSOCKET HANDLER (THIS IS THE FIX!)
// ──────────────────────────────────────────────────────────────
wss.on('connection', async (ws, req) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const path = url.pathname;

  // ── AGENT CONNECTION ──
  if (path === '/ws/agent') {
    const secretKey = url.searchParams.get('secret_key');
    if (!secretKey) return ws.close(1008, 'No secret_key');

    const computer = await Computer.query().where('secret_key', secretKey).first();
    if (!computer) return ws.close(1008, 'Invalid key');

    // Mark online
    await Computer.query().findById(computer.id).patch({ is_online: true, last_seen: new Date() });

    // Kill old connection
    const old = connections.agents.get(secretKey);
    if (old) old.ws.terminate();

    connections.agents.set(secretKey, { ws, computerId: computer.id });
    console.log(`Agent ONLINE → ${computer.display_name} (ID: ${computer.id})`);

    broadcast(computer.id, {
      type: 'status',
      online: true,
    });

    ws.on('message', async (raw) => {
      try {
        const data = JSON.parse(raw);
        // Save screenshot
        if (data.screenshot) {
          await Screenshot.query().insert({
            computer_id: computer.id,
            image_base64: data.screenshot.split(',')[1] // strip data:image/webp;base64,
          });
        }

        // Save stats
        if (data.stats) {
          await Activity.query().insert({
            computer_id: computer.id,
            cpu: data.stats.cpu || 0,
            ram: data.stats.ram_percent || 0,
            uptime: data.stats.uptime || 0,
            active_app: data.stats.active_window || null
          });
        }

        const payload = {
          type: data.type || 'status',
          online: true,
          screenshot: data.screenshot || null,
          stats: data.stats || null
        };

        // SEND TO ALL VIEWERS
        broadcast(computer.id, payload);
      } catch (e) {
        console.error("Bad message:", e);
      }
    });

    ws.on('close', async () => {
      connections.agents.delete(secretKey);
      await Computer.query().findById(computer.id).patch({ is_online: false });
      broadcast(computer.id, { type: 'status', online: false });
      console.log(`Agent OFFLINE → ${computer.display_name}`);
    });
  }

  // ── VIEWER CONNECTION ──
  else if (path.startsWith('/ws/viewer/')) {
    const computerId = parseInt(path.split('/ws/viewer/')[1]);
    if (isNaN(computerId)) return ws.close();

    if (!connections.viewers.has(computerId)) {
      connections.viewers.set(computerId, new Set());
    }
    connections.viewers.get(computerId).add(ws);

    // Send current status
    const pc = await Computer.query().findById(computerId);

    const screenshot = await Screenshot.query()
      .where("computer_id", computerId)
      .orderBy("captured_at", "desc")
      .first();

    const lastActivity = await Activity.query()
      .where("computer_id", computerId)
      .orderBy("timestamp", "desc")
      .first();

    ws.send(
      JSON.stringify({
        type: "status",
        online: !!pc?.is_online,
        screenshot: screenshot
          ? "data:image/webp;base64," + screenshot.image_base64
          : null,
        stats: lastActivity || null
      })
    );

    console.log(`Viewer connected to PC ${computerId}`);

    ws.on('close', () => {
      const set = connections.viewers.get(computerId);
      set?.delete(ws);
      if (set?.size === 0) connections.viewers.delete(computerId);
    });
  }
});

// ──────────────────────────────────────────────────────────────
// START SERVER
// ──────────────────────────────────────────────────────────────
const PORT = process.env.PORT || 5500;
server.listen(PORT, () => {
  console.log(`\nSPECTATOR SERVER RUNNING`);
  console.log(`→ http://localhost:${PORT}`);
  console.log(`→ Agent URL: ws://localhost:${PORT}/ws/agent?secret_key=YOUR_KEY`);
  console.log(`→ Viewer URL: ws://localhost:${PORT}/ws/viewer/1\n`);
});