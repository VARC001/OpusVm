import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import MongoClient
from Opus import app

# MongoDB setup
mongo_client = MongoClient("mongodb+srv://kunaalkumar0091:6qhyyQIyS2idoGFQ@cluster0.z2jge.mongodb.net/?retryWrites=true&w=majority")  # Replace with your MongoDB URI
db = mongo_client["auto_delete_bot"]
auth_collection = db["auth_users"]
delay_collection = db["delay_times"]


# Command to authorize a user in a group
@app.on_message(filters.command("mauth") & filters.group)
async def authorize_user(client: Client, message: Message):
    # Check if the command is used by an admin
    if not await is_admin(message):
        await message.reply("Only admins can authorize users.")
        return

    # Get the user to authorize
    try:
        user_id = message.reply_to_message.from_user.id
    except AttributeError:
        await message.reply("Reply to a user's message to authorize them.")
        return

    # Add the user to the authorized list for this group
    chat_id = message.chat.id
    auth_collection.update_one(
        {"chat_id": chat_id},
        {"$addToSet": {"user_ids": user_id}},
        upsert=True
    )
    await message.reply(f"User {user_id} has been authorized in this group.")

# Command to unauthorize a user in a group
@app.on_message(filters.command("munauth") & filters.group)
async def unauthorize_user(client: Client, message: Message):
    # Check if the command is used by an admin
    if not await is_admin(message):
        await message.reply("Only admins can unauthorize users.")
        return

    # Get the user to unauthorize
    try:
        user_id = message.reply_to_message.from_user.id
    except AttributeError:
        await message.reply("Reply to a user's message to unauthorize them.")
        return

    # Remove the user from the authorized list for this group
    chat_id = message.chat.id
    auth_collection.update_one(
        {"chat_id": chat_id},
        {"$pull": {"user_ids": user_id}}
    )
    await message.reply(f"User {user_id} has been unauthorized in this group.")

# Command to list authorized users in a group
@app.on_message(filters.command("mauthuserslist") & filters.group)
async def list_auth_users(client: Client, message: Message):
    chat_id = message.chat.id
    auth_data = auth_collection.find_one({"chat_id": chat_id})

    if auth_data and "user_ids" in auth_data:
        user_ids = auth_data["user_ids"]
        user_list = "\n".join([f"`{user_id}`" for user_id in user_ids])
        await message.reply(f"Authorized users in this group:\n{user_list}")
    else:
        await message.reply("No authorized users in this group.")

# Command to set the delay time for a group
@app.on_message(filters.command("setdelay") & filters.group)
async def set_delay(client: Client, message: Message):
    # Check if the command is used by an admin
    if not await is_admin(message):
        await message.reply("Only admins can set the delay time.")
        return

    # Extract the delay time from the command
    try:
        delay = int(message.command[1])  # /setdelay 5
        if delay < 1:
            await message.reply("Delay time must be at least 1 minute.")
            return

        # Store the delay time for this group
        chat_id = message.chat.id
        delay_collection.update_one(
            {"chat_id": chat_id},
            {"$set": {"delay": delay}},
            upsert=True
        )
        await message.reply(f"Auto-deletion delay set to {delay} minutes for this group.")

    except (IndexError, ValueError):
        await message.reply("Usage: /setdelay <time_in_minutes>")

# Handler for incoming media messages
@app.on_message(filters.group & (
    filters.photo | filters.video | filters.animation | filters.sticker | filters.voice | filters.document
))
async def handle_media(client: Client, message: Message):
    chat_id = message.chat.id

    # Check if the user is authorized
    auth_data = auth_collection.find_one({"chat_id": chat_id})
    if auth_data and "user_ids" in auth_data:
        user_id = message.from_user.id
        if user_id not in auth_data["user_ids"]:
            return  # Ignore media from unauthorized users

    # Get the delay time for this group
    delay_data = delay_collection.find_one({"chat_id": chat_id})
    if delay_data and "delay" in delay_data:
        delay = delay_data["delay"]
        await asyncio.sleep(delay * 60)  # Convert minutes to seconds

        # Delete the media message after the delay
        try:
            await message.delete()
            print(f"Deleted media in chat {chat_id} after {delay} minutes.")
        except Exception as e:
            print(f"Failed to delete media: {e}")

# Helper function to check if a user is an admin
async def is_admin(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    admins = await app.get_chat_members(chat_id, filter="administrators")
    return any(admin.user.id == user_id for admin in admins)

