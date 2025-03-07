import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from Opus import app 

delay_times = {}

@app.on_message(filters.command("setdelay"))
async def set_delay(client: Client, message: Message):
    try:
        delay = int(message.command[1])
        if delay < 1:
            await message.reply("ᴅᴇʟᴀʏ ᴛɪᴍᴇ ᴍᴜꜱᴛ ʙᴇ ᴀᴛ ʟᴇᴀꜱᴛ 1 ᴍɪɴᴜᴛᴇ.")
            return

        chat_id = message.chat.id
        delay_times[chat_id] = delay
        await message.reply(f"ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛɪᴏɴ ᴅᴇʟᴀʏ ꜱᴇᴛ ᴛᴏ {delay} ᴍɪɴᴜᴛᴇꜱ.")

    except (IndexError, ValueError):
        await message.reply("ᴜꜱᴀɢᴇ: /setdelay 5")

@app.on_message(filters.group & ~filters.poll & (
    filters.photo | filters.video | filters.video_note | filters.audio | 
    filters.voice | filters.document | filters.sticker | filters.animation | 
    filters.media_group))
async def handle_media(client: Client, message: Message):
    chat_id = message.chat.id

    if chat_id in delay_times:
        delay = delay_times[chat_id]
        await asyncio.sleep(delay * 60)

        try:
            await message.delete()
            print(f"ᴅᴇʟᴇᴛᴇᴅ ᴍᴇᴅɪᴀ ɪɴ ᴄʜᴀᴛ {chat_id} ᴀꜰᴛᴇʀ {delay} ᴍɪɴᴜᴛᴇꜱ.")
        except Exception as e:
            print(f"ꜰᴀɪʟᴇᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴍᴇᴅɪᴀ: {e}")
