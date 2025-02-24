from pyrogram.types import InlineKeyboardButton

import config
from Opus import app


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
            InlineKeyboardButton(text=_["S_B_6"], url=config.SUPPORT_CHANNEL),
            InlineKeyboardButton(text=_["S_B_2"], url=config.SUPPORT_CHAT),             
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
