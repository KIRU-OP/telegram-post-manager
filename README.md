# Telegram Post Manager

Telegram Bot API control panel for publishing to groups and channels where the bot has permission.

## Features
- Admin-only `/start` control center
- Register and remove approved destination chats
- Save text posts and publish to approved destinations
- Schedule saved posts (UTC)
- Delivery statistics and logs

## Safety and scope
This project uses the official Telegram Bot API. It does not log in to personal Telegram accounts or collect OTPs/session strings. Add the bot to each destination and grant posting permission. Only admin-approved destinations are used.

## Setup
1. Create a bot with @BotFather and copy its token.
2. Add the bot to your target groups/channels and grant posting permission.
3. Copy `.env.example` to `.env` and fill in the values.
4. Install Python 3.10+ and MongoDB, then run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

`ADMIN_IDS` is a comma-separated list of numeric Telegram user IDs. `MONGODB_URI` must point to a reachable MongoDB instance.

## Scheduling
Saved posts can be scheduled with the scheduler interface; times are UTC. Keep the process running for scheduled jobs to execute.

## Production notes
Use a process manager such as systemd, keep `.env` private, back up MongoDB, and monitor logs. This starter focuses on text posts; add media handling and persistent schedule storage before relying on it for critical publishing.