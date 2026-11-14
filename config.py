import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN', '').strip()
MONGODB_URI = os.getenv('MONGODB_URI', '').strip()
DATABASE_NAME = os.getenv('DATABASE_NAME', 'telegram_post_manager').strip()

def parse_admin_ids(raw):
    result = set()
    for item in raw.split(','):
        if item.strip():
            try:
                result.add(int(item.strip()))
            except ValueError as exc:
                raise ValueError('ADMIN_IDS must contain numeric IDs') from exc
    return result

ADMIN_IDS = parse_admin_ids(os.getenv('ADMIN_IDS', ''))
if not BOT_TOKEN: raise RuntimeError('BOT_TOKEN is missing in .env')
if not MONGODB_URI: raise RuntimeError('MONGODB_URI is missing in .env')
if not ADMIN_IDS: raise RuntimeError('Add your numeric Telegram user ID to ADMIN_IDS')