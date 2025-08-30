from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from configs import cfg
from database import add_created_channel
import random
import string
import asyncio
import time
import pyrogram.utils
from pyrogram.errors import FloodWait, UsernameOccupied
import os

pyrogram.utils.MIN_CHANNEL_ID = -1009147483647

# Initialize Bot Client
app = Client(
    "bot",
    api_id=cfg.API_ID,
    api_hash=cfg.API_HASH,
    bot_token=cfg.BOT_TOKEN
)

# Dictionary to hold multiple user session clients
session_clients = {}

for i in range(1, 31):
    session_key = f"session{i}"
    session_string = getattr(cfg, f"SESSION_STRING_{i}", None)
    if session_string:
        session_clients[session_key] = Client(
            session_key,
            api_id=cfg.API_ID,
            api_hash=cfg.API_HASH,
            session_string=session_string
        )

LOG_CHANNEL = cfg.LOG_CHANNEL
changeall_running = False
channel_last_updated = {}

async def log_to_channel(text: str):
    await asyncio.sleep(2)
    try:
        await app.send_message(LOG_CHANNEL, text)
    except Exception as e:
        print(f"Failed to log message: {e}")

def generate_random_string():
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choices(characters, k=2))

@app.on_message(filters.command("start"))
async def start_message(client: Client, message: Message):
    await message.reply_text(
        "Hello! Use /create, /change1, /changeall, /stopchangeall."
    )
    await log_to_channel(f"👋 Bot started by {message.from_user.mention} (ID: {message.from_user.id})")

@app.on_message(filters.command("create"))
async def create_channel(client: Client, message: Message):
    sudo_users = cfg.SUDO
    if message.from_user.id not in sudo_users:
        await message.reply_text("❌ Only sudo users can create channels.")
        return

    buttons = [
        [InlineKeyboardButton(f"Session {i}", callback_data=f"create_session{i}")]
        for i in range(1, 11) if f"session{i}" in session_clients
    ]
    await message.reply_text("Select session:", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex(r"^create_session(\d+)$"))
async def handle_create_callback(client, callback_query):
    session_number = callback_query.data.split("_")[-1]
    session_key = f"session{session_number}"
    selected_client = session_clients[session_key]
    try:
        channel = await selected_client.create_channel(
            title="hi",
            description="A private channel created by the bot."
        )
        add_created_channel(channel.id)
        await callback_query.message.reply_text(f"✅ Channel created in {session_key}: {channel.title}")
    except Exception as e:
        await callback_query.message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("change1"))
async def change_channel_link(client: Client, message: Message):
    sudo_users = cfg.SUDO
    if message.from_user.id not in sudo_users:
        await message.reply_text("❌ Only sudo users can change channel links.")
        return

    buttons = [
        [InlineKeyboardButton(f"Session {i}", callback_data=f"change1_session{i}")]
        for i in range(1, 11) if f"session{i}" in session_clients
    ]
    await message.reply_text("Select a session:", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex(r"^change1_session(\d+)$"))
async def handle_change1_callback(client, callback_query):
    session_number = callback_query.data.split("_")[-1]
    session_key = f"session{session_number}"
    selected_client = session_clients[session_key]
    try:
        channels = []
        async for dialog in selected_client.get_dialogs():
            if dialog.chat.username:
                channels.append(dialog.chat)

        if not channels:
            await callback_query.message.reply_text("❌ No channels with usernames found.")
            return

        buttons = [
            [InlineKeyboardButton(text=channel.title, callback_data=f"change1_{session_key}_{channel.id}")]
            for channel in channels
        ]
        await callback_query.message.reply_text(
            f"Select a channel from {session_key}:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await callback_query.message.reply_text(f"❌ Error: {e}")

@app.on_callback_query(filters.regex(r"^change1_session\d+_(-?\d+)$"))
async def on_channel_change_callback(client, callback_query):
    parts = callback_query.data.split("_")
    session_key = parts[1]
    channel_id = int(parts[2])
    selected_client = session_clients[session_key]

    try:
        channel = await selected_client.get_chat(channel_id)
        old_username = channel.username
        new_suffix = generate_random_string()
        new_username = f"{old_username[:-3]}{new_suffix}"

        await selected_client.set_chat_username(channel.id, new_username)
        await callback_query.message.reply_text(f"✅ Changed to: https://t.me/{new_username}")

    except Exception as e:
        await callback_query.message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("changeall"))
async def changeall_command(client: Client, message: Message):
    global changeall_running
    sudo_users = cfg.SUDO

    if message.chat.id != LOG_CHANNEL and message.from_user and message.from_user.id not in sudo_users:
        await message.reply_text("❌ Only sudo users can run this command.")
        return

    if changeall_running:
        await message.reply_text("⚠️ Changeall is already running.")
        return

    changeall_running = True
    with open("changeall.flag", "w") as f:
        f.write("running")

    await message.reply_text("✅ Started changing usernames for ALL sessions.")
    await log_to_channel("🚀 Changeall started.")

    async def process_session(session_key, selected_client):
        while changeall_running:
            try:
                channels = []
                async for dialog in selected_client.get_dialogs():
                    if dialog.chat.username:
                        channels.append(dialog.chat)

                for channel in channels:
                    if not changeall_running:
                        break
                    old_username = channel.username
                    new_suffix = generate_random_string()
                    new_username = f"{old_username[:max(5, len(old_username) - 2)]}{new_suffix}"
                    try:
                        await selected_client.set_chat_username(channel.id, new_username)
                        await log_to_channel(f"✅ {session_key}: @{old_username} → @{new_username}")
                    except FloodWait as e:
                        await log_to_channel(f"❌ {session_key} Rate limit exceeded. Waiting {e.value}s.")
                        await asyncio.sleep(e.value)
                        continue
                    except UsernameOccupied:
                        await log_to_channel(f"⚠️ {session_key}: @{new_username} already taken.")
                        continue
                    except Exception as e:
                        await log_to_channel(f"❌ {session_key} error: {e}")
                        continue

                    await asyncio.sleep(60 * 90)  # 1 hour delay per channel
            except Exception as e:
                await asyncio.sleep(2)

    for session_key, selected_client in session_clients.items():
        asyncio.create_task(process_session(session_key, selected_client))

                        
@app.on_message(filters.command("stopchangeall"))
async def stop_changeall(client: Client, message: Message):
    global changeall_running
    sudo_users = cfg.SUDO
    if message.from_user.id not in sudo_users:
        await message.reply_text("❌ Only sudo users can stop the process.")
        return

    changeall_running = False
    await message.reply_text("🛑 Changeall process stopped.")
    await log_to_channel(f"🛑 Changeall process stopped by {message.from_user.mention}.")

# Start all session clients
for client in session_clients.values():
    client.start()

app.run()
