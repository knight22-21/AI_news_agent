import { makeWASocket, useMultiFileAuthState, fetchLatestBaileysVersion } from '@whiskeysockets/baileys';
import qrcode from 'qrcode-terminal';
import axios from 'axios';
import fs from 'fs';

// Load allowed group IDs from messages.json
const groupData = JSON.parse(fs.readFileSync('./messages.json', 'utf-8'));
console.log('✅ Authorized group access loaded.');

async function startListener() {
  const { state, saveCreds } = await useMultiFileAuthState('auth_info_listener');
  const { version } = await fetchLatestBaileysVersion();

  const sock = makeWASocket({
    version,
    auth: state,
  });

  sock.ev.on('creds.update', saveCreds);

  sock.ev.on('connection.update', (update) => {
    const { connection, qr } = update;

    if (qr) {
      console.log('📲 Scan the QR code to log in:');
      qrcode.generate(qr, { small: true });
    }

    if (connection === 'close') {
      console.log('🔄 Connection closed. Reconnecting...');
      startListener(); // Restart listener
    } else if (connection === 'open') {
      console.log('✅ Bot is connected and ready!');
    }
  });

  sock.ev.on('messages.upsert', async ({ messages }) => {
    const msg = messages[0];
    if (!msg.message) return;

    const body = msg.message.conversation || msg.message.extendedTextMessage?.text || '';
    const trimmedBody = body.trim();
    const jid = msg.key.remoteJid;

    // Only respond to the "!news" command
    if (trimmedBody !== "!news") {
      console.log('ℹ️ Non-news command ignored.');
      return;
    }

    const groupAllowed = groupData.find(group => group.groupId === jid);
    if (!groupAllowed) {
      console.log('⛔ Unauthorized group tried to use the command.');
      await sock.sendMessage(jid, { text: "🚫 This group is not allowed to run this command." });
      return;
    }

    try {
      const metadata = await sock.groupMetadata(jid);
      const sender = msg.key.participant || msg.key.remoteJid;

      // Allow bot itself (QR scanner) to issue the command
      const botJid = sock.user?.id;
      const isFromBot = sender === botJid;

      const participant = metadata.participants.find(p => p.id === sender);
      const isAdmin = participant?.admin === 'admin' || participant?.admin === 'superadmin';

      if (!isAdmin && !isFromBot) {
        console.log('⛔ Unauthorized user tried to run the command.');
        await sock.sendMessage(jid, { text: "🚫 Only group admins can run this command." });
        return;
      }

      console.log('✅ Running AI News agent via API...');
      try {
        const response = await axios.post('http://localhost:8000/news', {
          command: 'get ai news'
        });

        const { data } = response;
        if (data.success) {
          const summary = data.summary.raw || data.summary || JSON.stringify(data, null, 2);
          const summaryText = typeof summary === 'string' ? summary : JSON.stringify(summary, null, 2);
          const chunks = summaryText.match(/[\s\S]{1,3000}/g) || [];

          for (const chunk of chunks) {
            await sock.sendMessage(jid, { text: chunk });
          }
        } else {
          await sock.sendMessage(jid, { text: "⚠️ Error: " + data.error });
        }
      } catch (err) {
        console.error("❌ Error during API call:", err);
        await sock.sendMessage(jid, { text: "⚠️ Failed to connect to AI News API." });
      }

    } catch (err) {
      console.error("❌ Error while processing command:", err);
      await sock.sendMessage(jid, { text: "⚠️ An unexpected error occurred while handling the command." });
    }
  });
}

startListener();
