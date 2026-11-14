from datetime import datetime, timezone
from bson import ObjectId
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from app.db import destinations, posts, deliveries
from app.keyboards import main_menu, back_menu, destination_actions, post_actions
from app.scheduler import scheduler, deliver_post
from config import ADMIN_IDS

router = Router()
class Flow(StatesGroup):
    waiting_destination = State()
    waiting_post_text = State()
    waiting_schedule = State()

def is_admin(user_id): return user_id in ADMIN_IDS
async def deny(target):
    if isinstance(target, Message): await target.answer('⛔ Admin only.')
    else: await target.answer('⛔ Admin only.', show_alert=True)

@router.message(CommandStart())
async def start(message: Message):
    if not is_admin(message.from_user.id): return await deny(message)
    await message.answer('👋 Welcome to Telegram Post Manager!\nManage approved destinations, saved posts and scheduled publishing.', reply_markup=main_menu())

@router.callback_query(F.data == 'menu:home')
async def home(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id): return await deny(call)
    await state.clear()
    await call.message.answer('🛠 Main Menu — Control Center', reply_markup=main_menu())
    await call.answer()

@router.callback_query(F.data == 'dest:add')
async def add_destination(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id): return await deny(call)
    await state.set_state(Flow.waiting_destination)
    await call.message.answer('Send numeric chat ID. The bot must already be added and have posting permission.')
    await call.answer()

@router.message(Flow.waiting_destination)
async def save_destination(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id): return await deny(message)
    try:
        chat_id = int((message.text or '').strip())
        chat = await bot.get_chat(chat_id)
        await bot.get_chat_member(chat_id, bot.id)
        await destinations.update_one({'chat_id': chat_id}, {'$set': {'chat_id': chat_id, 'title': chat.title or str(chat_id), 'approved': True, 'added_by': message.from_user.id}}, upsert=True)
        await state.clear()
        await message.answer('✅ Destination saved: ' + (chat.title or str(chat_id)), reply_markup=main_menu())
    except Exception as exc:
        await message.answer('Could not verify destination. Add the bot and grant posting permission. Details: ' + str(exc)[:200])

@router.callback_query(F.data == 'dest:list')
async def list_destinations(call: CallbackQuery):
    if not is_admin(call.from_user.id): return await deny(call)
    rows = await destinations.find({'approved': True}).to_list(length=100)
    if not rows: await call.message.answer('No approved destinations yet.', reply_markup=back_menu())
    for row in rows:
        await call.message.answer(f"📍 {row.get('title', 'Destination')}\nID: {row['chat_id']}", reply_markup=destination_actions(row['chat_id']))
    await call.answer()

@router.callback_query(F.data.startswith('dest:remove:'))
async def remove_destination(call: CallbackQuery):
    if not is_admin(call.from_user.id): return await deny(call)
    chat_id = int(call.data.rsplit(':', 1)[1])
    await destinations.delete_one({'chat_id': chat_id})
    await call.answer('Destination removed.')
    await call.message.answer('✅ Destination removed.', reply_markup=main_menu())

@router.callback_query(F.data == 'post:create')
async def create_post(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id): return await deny(call)
    await state.set_state(Flow.waiting_post_text)
    await call.message.answer('Send the text you want to save as a post.')
    await call.answer()

@router.message(Flow.waiting_post_text)
async def save_post(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return await deny(message)
    text = (message.text or '').strip()
    if not text: return await message.answer('Please send a text message.')
    result = await posts.insert_one({'text': text, 'created_by': message.from_user.id, 'created_at': datetime.now(timezone.utc)})
    await state.clear()
    await message.answer('✅ Post saved. ID: ' + str(result.inserted_id), reply_markup=main_menu())

@router.callback_query(F.data == 'post:list')
async def list_posts(call: CallbackQuery):
    if not is_admin(call.from_user.id): return await deny(call)
    rows = await posts.find().sort('_id', -1).to_list(length=20)
    if not rows: await call.message.answer('No saved posts yet.', reply_markup=back_menu())
    for row in rows: await call.message.answer('📝 ' + str(row['_id']) + '\n\n' + row['text'][:700], reply_markup=post_actions(str(row['_id'])))
    await call.answer()

@router.callback_query(F.data == 'post:send')
async def choose_post(call: CallbackQuery):
    if not is_admin(call.from_user.id): return await deny(call)
    rows = await posts.find().sort('_id', -1).to_list(length=10)
    if not rows: await call.message.answer('No saved posts. Create one first.')
    for row in rows: await call.message.answer('Send this post?\n\n' + row['text'][:700], reply_markup=post_actions(str(row['_id'])))
    await call.answer()

@router.callback_query(F.data.startswith('post:send:'))
async def send_post(call: CallbackQuery, bot: Bot):
    if not is_admin(call.from_user.id): return await deny(call)
    post_id = call.data.rsplit(':', 1)[1]
    await deliver_post(bot, post_id)
    post = await posts.find_one({'_id': ObjectId(post_id)})
    report = (post or {}).get('last_delivery', {})
    await call.message.answer(f"📊 Delivery finished.\nSuccessful: {report.get('sent', 0)}\nFailed: {report.get('failed', 0)}", reply_markup=main_menu())
    await call.answer('Send completed.')

@router.callback_query(F.data == 'schedule:list')
async def schedule_list(call: CallbackQuery):
    if not is_admin(call.from_user.id): return await deny(call)
    jobs = scheduler.get_jobs()
    if not jobs: await call.message.answer('No scheduled posts.', reply_markup=back_menu())
    else: await call.message.answer('📅 Scheduled jobs (UTC):\n' + '\n'.join(f'{j.id} — {j.next_run_time}' for j in jobs), reply_markup=back_menu())
    await call.answer()

@router.callback_query(F.data.startswith('post:schedule:'))
async def schedule_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id): return await deny(call)
    await state.update_data(post_id=call.data.rsplit(':', 1)[1])
    await state.set_state(Flow.waiting_schedule)
    await call.message.answer('Send schedule time in UTC: YYYY-MM-DD HH:MM')
    await call.answer()

@router.message(Flow.waiting_schedule)
async def schedule_save(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id): return await deny(message)
    try:
        run_at = datetime.strptime(message.text.strip(), '%Y-%m-%d %H:%M').replace(tzinfo=timezone.utc)
        if run_at <= datetime.now(timezone.utc): raise ValueError('Time must be in the future')
        post_id = (await state.get_data())['post_id']
        scheduler.add_job(deliver_post, 'date', run_date=run_at, args=[bot, post_id], id=f'post-{post_id}-{int(run_at.timestamp())}', replace_existing=True)
        await state.clear()
        await message.answer(f'✅ Scheduled for {run_at:%Y-%m-%d %H:%M} UTC', reply_markup=main_menu())
    except Exception as exc: await message.answer('Invalid schedule: ' + str(exc))

@router.callback_query(F.data == 'stats')
async def stats(call: CallbackQuery):
    if not is_admin(call.from_user.id): return await deny(call)
    d = await destinations.count_documents({'approved': True})
    p = await posts.count_documents({})
    s = await deliveries.count_documents({'status': 'sent'})
    f = await deliveries.count_documents({'status': 'failed'})
    await call.message.answer(f'📊 Statistics\n\nDestinations: {d}\nSaved posts: {p}\nSuccessful deliveries: {s}\nFailed deliveries: {f}', reply_markup=back_menu())
    await call.answer()