
## AI News WhatsApp Agent

This project fetches the latest AI-related news (LLMs, RAG, AI agents) using the NewsAPI and sends a summarized version directly to a WhatsApp group using the Baileys library.

---

### Project Structure

* `main.py` — Triggers the CrewAI pipeline and sends the summary to WhatsApp.
* `ai_news.py` — (Optional) FastAPI interface to trigger the bot via HTTP.
* `bot.js` — Connects to WhatsApp and sends messages to a specific group.
* `messages.json` — Stores WhatsApp `groupId` to send the message to.

---

### Setup Instructions

1. **Install Python dependencies**

```bash
pip install -r requirements.txt
```

2. **Install Node.js dependencies**

```bash
npm install
```

3. **Add your `.env` file**

```
NEWS_API_KEY=your_newsapi_key_here
```

4. **Add your WhatsApp group ID**
   In `messages.json`:

```json
[
  {
    "groupId": "your_group_id@g.us"
  }
]
```

---

### Running the Bot

Start the bot manually from PowerShell or terminal:

```bash
python main.py
```

> This will:
>
> * Fetch the latest AI news.
> * Summarize it using CrewAI.
> * Send it to your configured WhatsApp group.

---

### First-Time WhatsApp Login

When you run the bot for the first time, you'll be prompted to **scan a QR code**. This logs the bot into WhatsApp Web.

---

### Tech Stack

* Python: CrewAI, FastAPI, NewsAPI
* Node.js: Baileys (WhatsApp Web API)

---

