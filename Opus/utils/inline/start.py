from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

import config
from Opus import app

ABOUT_TEXT = "This is MusicBot, a powerful Telegram music streaming bot."

def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_1"], url=f"https://t.me/{app.username}?startgroup=true&admin=delete_messages+invite_users"
            ),
            InlineKeyboardButton(text=_["S_B_2"], url=config.SUPPORT_CHAT),
        ],
    ]
    return buttons

def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true&admin=delete_messages+invite_users",
            )
        ],
        [InlineKeyboardButton(text=_["S_B_4"], callback_data="settings_back_helper")],
        [
            InlineKeyboardButton(text=_["S_B_11"], user_id=config.OWNER_ID),
            InlineKeyboardButton("About", callback_data="about")             
        ],
        [
            InlineKeyboardButton(text=_["S_B_11"], user_id=config.OWNER_ID),   
            InlineKeyboardButton(
                text=_["S_B_12"],
                url=f"https://t.me/STORM_TECHH/711",
            )            
        ],
    ]      
    return buttons

@app.on_callback_query(filters.regex("about"))
async def about_callback(client: Client, query: CallbackQuery):
    await query.answer()
    await query.message.edit_text(
        ABOUT_TEXT,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Back", callback_data="settings_back_helper")]
        ])
    )
