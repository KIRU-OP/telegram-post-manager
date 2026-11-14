from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bson import ObjectId
from app.db import destinations, posts, deliveries

scheduler = AsyncIOScheduler(timezone='UTC')

async def deliver_post(bot, post_id):
    post = await posts.find_one({'_id': ObjectId(post_id)})
    if not post: return
    sent = failed = 0
    async for dest in destinations.find({'approved': True}):
        try:
            await bot.send_message(chat_id=dest['chat_id'], text=post['text'])
            sent += 1
            status, error = 'sent', None
        except Exception as exc:
            failed += 1
            status, error = 'failed', str(exc)[:500]
        await deliveries.insert_one({'post_id': post_id, 'chat_id': dest['chat_id'], 'status': status, 'error': error, 'created_at': datetime.now(timezone.utc)})
    await posts.update_one({'_id': post['_id']}, {'$set': {'last_delivery': {'sent': sent, 'failed': failed}}})

def start_scheduler():
    if not scheduler.running: scheduler.start()