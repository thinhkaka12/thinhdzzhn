/**
 * Simple Node.js Express backend to receive IP info and send to Telegram Bot
 * 
 * Usage:
 * 1. Save this file as ip-telegram-backend.js
 * 2. Run 'npm init -y' in the same directory
 * 3. Run 'npm install express cors node-fetch@2'
 * 4. Run 'node ip-telegram-backend.js'
 * 5. Make sure your frontend's backendEndpoint points to http://localhost:3000/collect-ip
 */

const express = require('express');
const cors = require('cors');
const fetch = require('node-fetch');

const app = express();

// Replace with your Telegram bot token and chat ID (numeric, no #)
const TELEGRAM_BOT_TOKEN = '7657217421:AAFcCRGCbDARpPVw8h-WvJfQ5FFcoCVfL1I';
const TELEGRAM_CHAT_ID = '7657217421';

const TELEGRAM_API_URL = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;

app.use(cors()); // Enable CORS for all origins. Adjust in prod for security.
app.use(express.json());

app.post('/collect-ip', async (req, res) => {
  const { ip } = req.body;
  if (!ip) {
    return res.status(400).json({ error: 'Missing ip field' });
  }

  const messageText = `📡 New visitor IP: ${ip}\nTime: ${new Date().toISOString()}`;

  try {
    const tgResponse = await fetch(TELEGRAM_API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: TELEGRAM_CHAT_ID,
        text: messageText
      })
    });

    if (!tgResponse.ok) {
      const text = await tgResponse.text();
      console.error('Telegram API error:', text);
      return res.status(502).json({ error: 'Failed to send message to Telegram' });
    }

    res.json({ success: true, message: 'IP sent to Telegram' });
  } catch (err) {
    console.error('Error sending Telegram message:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Health check endpoint
app.get('/', (req, res) => {
  res.send('IP Telegram backend is running.');
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`IP Telegram backend listening on port ${PORT}`);
});

                                                        
