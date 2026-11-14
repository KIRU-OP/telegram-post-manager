from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='➕ Add Destination', callback_data='dest:add'), InlineKeyboardButton(text='⚙️ Manage Destinations', callback_data='dest:list')],
        [InlineKeyboardButton(text='📝 Create Post', callback_data='post:create'), InlineKeyboardButton(text='📚 Saved Posts', callback_data='post:list')],
        [InlineKeyboardButton(text='📢 Send Post', callback_data='post:send'), InlineKeyboardButton(text='📅 Scheduled Posts', callback_data='schedule:list')],
        [InlineKeyboardButton(text='📊 Statistics', callback_data='stats')],
    ])

def back_menu():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='⬅️ Main Menu', callback_data='menu:home')]])

def destination_actions(chat_id):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🗑 Remove', callback_data=f'dest:remove:{chat_id}')], [InlineKeyboardButton(text='⬅️ Back', callback_data='dest:list')]])

def post_actions(post_id):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='📢 Send this post', callback_data=f'post:send:{post_id}')], [InlineKeyboardButton(text='⬅️ Back', callback_data='post:list')]])