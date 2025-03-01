import random
from pyrogram import Client
from pyrogram.types import Message
from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
)
from config import LOGGER_ID as LOG_GROUP_ID
from Opus import app
from Opus.core.userbot import Userbot
from Opus.utils.database import delete_served_chat, add_served_chat
from Opus.utils.database import get_assistant


photo = [
    "https://telegra.ph//file/0879fbdb307005c1fa8ab.jpg",
    "https://telegra.ph//file/19e3a9d5c0985702497fb.jpg",
    "https://telegra.ph//file/b5fa277081dddbddd0b12.jpg",
    "https://telegra.ph//file/96e96245fe1afb82d0398.jpg",
    "https://telegra.ph//file/fb140807129a3ccb60164.jpg",
    "https://telegra.ph//file/09c9ea0e2660efae6f62a.jpg",
    "https://telegra.ph//file/3b59b15e1914b4fa18b71.jpg",
    "https://telegra.ph//file/efb26cc17eef6fe82d910.jpg",
    "https://telegra.ph//file/ab4925a050e07b00f63c5.jpg",
    "https://telegra.ph//file/d169a77fd52b46e421414.jpg",
    "https://telegra.ph//file/dab9fc41f214f9cded1bb.jpg",
    "https://telegra.ph//file/e05d6e4faff7497c5ae56.jpg",
    "https://telegra.ph//file/1e54f0fff666dd53da66f.jpg",
    "https://telegra.ph//file/18e98c60b253d4d926f5f.jpg",
    "https://telegra.ph//file/b1f7d9702f8ea590b2e0c.jpg",
    "https://telegra.ph//file/7bb62c8a0f399f6ee1f33.jpg",
    "https://telegra.ph//file/dd00c759805082830b6b6.jpg",
    "https://telegra.ph//file/3b996e3241cf93d102adc.jpg",
    "https://telegra.ph//file/610cc4522c7d0f69e1eb8.jpg",
    "https://telegra.ph//file/bc97b1e9bbe6d6db36984.jpg",
    "https://telegra.ph//file/2ddf3521636d4b17df6dd.jpg",
    "https://telegra.ph//file/72e4414f618111ea90a57.jpg",
    "https://telegra.ph//file/a958417dcd966d341bfe2.jpg",
    "https://telegra.ph//file/0afd9c2f70c6328a1e53a.jpg",
    "https://telegra.ph//file/82ff887aad046c3bcc9a3.jpg",
    "https://telegra.ph//file/8ba64d5506c23acb67ff4.jpg",
    "https://telegra.ph//file/8ba64d5506c23acb67ff4.jpg",
    "https://telegra.ph//file/a7cba6e78bb63e1b4aefb.jpg",
    "https://telegra.ph//file/f8ba75bdbb9931cbc8229.jpg",
    "https://telegra.ph//file/07bb5f805178ec24871d3.jpg"
]


from strings.__init__ import LOGGERS


@app.on_message(filters.new_chat_members, group=2)
async def join_watcher(_, message):
    try:
        userbot = await get_assistant(message.chat.id)
        chat = message.chat
        for members in message.new_chat_members:
            if members.id == app.id:
                count = await app.get_chat_members_count(chat.id)
                username = (
                    message.chat.username if message.chat.username else "ᴘʀɪᴠᴀᴛᴇ ɢʀᴏᴜᴘ"
                )
                msg = f"● ᴊᴏɪɴᴇᴅ ᴀ ɴᴇᴡ ɢʀᴏᴜᴘ ●\n\n<b>ᴄʜᴀᴛ ɴᴀᴍᴇ: {message.chat.title}</b>\n<b>ᴄʜᴀᴛ ɪᴅ: {message.chat.id}</b>\n<b>ᴄʜᴀᴛ ᴍᴇᴍʙᴇʀꜱ: {count}</b>"
                await app.send_photo(
                    LOG_GROUP_ID,
                    photo=random.choice(photo),
                    caption=msg,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    f"ᴀᴅᴅ ᴍᴇ",
                                    url=f"https://t.me/StormMusicPlayer_bot?startgroup=true&admin=delete_messages+invite_users",
                                )
                            ]
                        ]
                    ),
                )
                await add_served_chat(message.chat.id)
                await userbot.join_chat(f"{username}")
                oks = await userbot.send_message(LOGGERS, f"/start")
                Ok = await userbot.send_message(
                    LOGGERS, f"#{app.username}\n@{app.username}"
                )
                await oks.delete()
                await asyncio.sleep(2)
                await Ok.delete()

    except Exception as e:
        print(f"Error: {e}")
