import { makeWASocket, useMultiFileAuthState, fetchLatestBaileysVersion } from '@whiskeysockets/baileys';
import qrcode from 'qrcode-terminal';
import fs from 'fs';

async function sendSummaryToGroup(groupId, summaryText) {
  const { state, saveCreds } = await useMultiFileAuthState('auth_info_listener');
  const { version } = await fetchLatestBaileysVersion();
  const sock = makeWASocket({
    version,
    auth: state,
  });

  sock.ev.on('creds.update', saveCreds);

  sock.ev.on('connection.update', ({ connection, qr, lastDisconnect }) => {
    if (qr) {
      console.log("📱 Scan this QR to log into WhatsApp:");
      qrcode.generate(qr, { small: true });
    }

    if (connection === 'close') {
      const reason = lastDisconnect?.error?.output?.payload?.message || "unknown reason";
      console.error(`Connection closed: ${reason}`);
      process.exit(1);
    }

    if (connection === 'open') {
      console.log("WhatsApp connected. Sending summary...");
    }
  });

  await new Promise(resolve => {
    sock.ev.on('connection.update', ({ connection }) => {
      if (connection === 'open') resolve();
    });
  });

  const chunks = summaryText.match(/[\s\S]{1,3000}/g) || [];
  for (const chunk of chunks) {
    await sock.sendMessage(groupId, { text: chunk });
  }

  console.log(`Summary sent to group: ${groupId}`);
  process.exit(0);
}

if (process.argv[2] === "send") {
  const groupId = process.argv[3];

  if (!groupId) {
    console.error("Usage: node bot.js send <groupId>");
    process.exit(1);
  }

  let summary = '';
  process.stdin.setEncoding('utf-8');
  process.stdin.on('data', chunk => (summary += chunk));
  process.stdin.on('end', () => {
    if (!summary.trim()) {
      console.error("No summary provided via stdin.");
      process.exit(1);
    }
    sendSummaryToGroup(groupId, summary.trim());
  });
}
