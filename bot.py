from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from configs import cfg
from database import add_created_channel
import random
import string
import asyncio
import pyrogram.utils
from pyrogram.errors import FloodWait
from pyrogram.raw import functions, types

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
reportall_running = False

async def log_to_channel(text: str):
    try:
        await app.send_message(LOG_CHANNEL, text)
    except Exception as e:
        print(f"Failed to log message: {e}")

# Reporting function
async def report_channel(client, channel_id: int, reason: str = "spam"):
    reason_map = {
        "spam": types.InputReportReasonSpam(),
        "violence": types.InputReportReasonViolence(),
        "porn": types.InputReportReasonPornography(),
        "child": types.InputReportReasonChildAbuse(),
        "copyright": types.InputReportReasonCopyright(),
        "other": types.InputReportReasonOther()
    }
    reason_obj = reason_map.get(reason, types.InputReportReasonSpam())

    try:
        peer = await client.resolve_peer(channel_id)
        result = await client.invoke(
            functions.account.ReportPeer(
                peer=peer,
                reason=reason_obj,
                message="Reported automatically by bot"
            )
        )
        return "✅ Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return f"⏳ FloodWait {e.value}s"
    except Exception as e:
        return f"❌ Error: {e}"

@app.on_message(filters.command("start"))
async def start_message(client: Client, message: Message):
    await message.reply_text(
        "Hello! Use:\n"
        "/report1 - Report from one session\n"
        "/reportall - Report from all sessions continuously\n"
        "/stopreportall - Stop reporting"
    )
    await log_to_channel(f"👋 Bot started by {message.from_user.mention} (ID: {message.from_user.id})")

# Report from one session
@app.on_message(filters.command("report1"))
async def report1_command(client: Client, message: Message):
    sudo_users = cfg.SUDO
    if message.from_user.id not in sudo_users:
        await message.reply_text("❌ Only sudo users can report.")
        return

    if len(message.command) < 3:
        await message.reply_text("Usage: /report1 <channel_id or @username> <reason>")
        return

    target = message.command[1]
    reason = message.command[2].lower()

    buttons = [
        [InlineKeyboardButton(f"Session {i}", callback_data=f"report1_session{i}_{target}_{reason}")]
        for i in range(1, 11) if f"session{i}" in session_clients
    ]
    await message.reply_text("Select session:", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex(r"^report1_session(\d+)_([^_]+)_(\w+)$"))
async def handle_report1_callback(client, callback_query):
    parts = callback_query.data.split("_")
    session_number = parts[1]
    target = parts[2]
    reason = parts[3]
    session_key = f"session{session_number}"
    selected_client = session_clients[session_key]

    try:
        if target.startswith("@"):
            chat = await selected_client.get_chat(target)
            channel_id = chat.id
        else:
            channel_id = int(target)

        result = await report_channel(selected_client, channel_id, reason)
        await callback_query.message.reply_text(f"{session_key} → Reported {target} for {reason}\n{result}")
    except Exception as e:
        await callback_query.message.reply_text(f"❌ Error: {e}")

# Report from all sessions continuously
@app.on_message(filters.command("reportall"))
async def reportall_command(client: Client, message: Message):
    global reportall_running
    sudo_users = cfg.SUDO

    if message.from_user.id not in sudo_users:
        await message.reply_text("❌ Only sudo users can run this command.")
        return

    if reportall_running:
        await message.reply_text("⚠️ Reportall is already running.")
        return

    if len(message.command) < 3:
        await message.reply_text("Usage: /reportall <channel_id or @username> <reason>")
        return

    target = message.command[1]
    reason = message.command[2].lower()
    reportall_running = True

    await message.reply_text("🚀 Started reporting from ALL sessions.")
    await log_to_channel(f"🚀 Reportall started for {target} with reason {reason}")

    async def process_session(session_key, selected_client):
        global reportall_running
        while reportall_running:
            try:
                if target.startswith("@"):
                    chat = await selected_client.get_chat(target)
                    channel_id = chat.id
                else:
                    channel_id = int(target)

                result = await report_channel(selected_client, channel_id, reason)
                await log_to_channel(f"{session_key} → {target} → {reason} → {result}")

                await asyncio.sleep(60 * 30)  # wait 30 minutes between reports per session
            except Exception as e:
                await log_to_channel(f"❌ {session_key} error: {e}")
                await asyncio.sleep(10)

    for session_key, selected_client in session_clients.items():
        asyncio.create_task(process_session(session_key, selected_client))

# Stop reporting
@app.on_message(filters.command("stopreportall"))
async def stop_reportall(client: Client, message: Message):
    global reportall_running
    sudo_users = cfg.SUDO
    if message.from_user.id not in sudo_users:
        await message.reply_text("❌ Only sudo users can stop reporting.")
        return

    reportall_running = False
    await message.reply_text("🛑 Reportall process stopped.")
    await log_to_channel(f"🛑 Reportall stopped by {message.from_user.mention}")

# Start all session clients
for client in session_clients.values():
    client.start()

app.run()
