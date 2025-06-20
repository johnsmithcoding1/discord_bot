# Discord Moderation, Logging, and Utility Bot

Welcome! This guide will help you set up and use your advanced Discord bot with moderation, logging, ticketing, training, role management, and fun commands.

---

## Features

- **Moderation:** Ban, kick, timeout, purge, change nicknames, etc.
- **Role Management:** Give, remove, and temporarily assign roles.
- **Ticket System:** Create, claim, close, and transcript tickets with dropdown UI.
- **Training Sessions:** Schedule and manage training events with attendance tracking.
- **Logging:** Member joins/leaves, bans, kicks, message edits/deletes, channel changes, and more.
- **Fun/Troll Commands:** Ghost ping, flip text, fake ban, scramble names, ghost typing, and more.
- **Slash Commands:** All commands use Discord's modern slash command system.

---

## Requirements

- Python 3.10 or higher
- A Discord Bot Token from the [Discord Developer Portal](https://discord.com/developers/applications)

### Required Python Packages
Install these with:
```sh
pip install -U discord.py python-dotenv
```

---

## Setup Instructions

### 1. Clone or Download the Bot Files
- Place all files in a folder, e.g.:
  - `bot.py`
  - `config.json`
  - `.env`
  - `cogs/` (with all cog files inside)

### 2. Add Your Bot Token
- Create a file named `.env` in the same folder as `bot.py`.
- Add this line (replace with your actual token):
  ```
  DISCORD_BOT_TOKEN=your_token_here
  ```

### 3. Configure Logging Channel
- Open `config.json` and set the `log_channel` to your desired channel ID:
  ```json
  {
    "log_channel": 123456789012345678
  }
  ```
- To get a channel ID: In Discord, enable Developer Mode (User Settings > Advanced), right-click the channel, and select "Copy ID".

### 4. Run the Bot
- In your terminal, navigate to the folder with `bot.py`:
  ```sh
  cd path/to/your/bot/folder
  python bot.py
  ```

### 5. Invite the Bot to Your Server
- In the Discord Developer Portal, go to OAuth2 > URL Generator.
- Select `bot` as a scope and add these permissions:
  - Send Messages
  - Manage Messages
  - Ban Members
  - Kick Members
  - Manage Nicknames
  - Moderate Members (Timeout)
  - Manage Roles
  - Manage Channels
  - View Channels
  - Read Message History
- Copy the generated link, open it in your browser, and invite the bot.

---

## Slash Commands List

### Moderation
- `/ban` — Ban a member
- `/kick` — Kick a member
- `/nickname` — Change a member's nickname
- `/hush` — Timeout a member
- `/purge` — Delete all messages in a channel
- `/ping` — Test if the bot is alive

### Roles
- `/giverole` — Give a role to a member
- `/removerole` — Remove a role from a member
- `/temprole` — Temporarily give a role to a member

### Tickets
- `/ticketpanel` — Create a ticket panel with dropdown

### Training
- `/training` — Schedule a training session with attendance

### Fun/Troll
- `/ghostping` — Ghost ping a user
- `/flip` — Flip your text upside down
- `/fakeban` — Fake ban someone for fun
- `/scramble` — Scramble a member's display name
- `/trolltype` — Pretend the bot is typing forever
- `/creepjoin` — Bot joins and leaves your VC
- `/ghost` — Start ghost typing as a user
- `/ghost_stop` — Stop ghost typing

---

## Logging
- Member join/leave, bans, kicks
- Message edits/deletes
- Channel create/delete/rename
- Role changes
- Voice channel join/leave/move

---

## Troubleshooting

- **Bot does not respond?**
  - Make sure your bot is online and has the correct permissions in your server.
  - Check your `.env` and `config.json` for correct values.
- **Slash commands not showing up?**
  - Global commands can take up to 1 hour to appear everywhere. Try restarting the bot and waiting.
  - Make sure you are not using guild-only sync in your code.
- **Logs not showing?**
  - Ensure the `log_channel` ID is correct and the bot can send messages there.
- **Permission errors?**
  - The bot's role must be high enough and have the required permissions.
- **Python errors?**
  - Ensure you installed all required packages and are running Python 3.10 or higher.

---

## File Structure Example
```
/your-bot-folder
  |-- bot.py
  |-- config.json
  |-- .env
  |-- cogs/
      |-- moderation.py
      |-- logging.py
      |-- roles.py
      |-- tickets.py
      |-- training.py
      |-- troll.py
```

---

## Need Help?
If you have issues or want to add features, open an issue or contact the developer!
