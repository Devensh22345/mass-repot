from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from configs import cfg
from pyrogram.raw import functions, types
import asyncio
import random

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
report_states = {}  # user_id -> state data

async def log_to_channel(text: str):
    try:
        await app.send_message(LOG_CHANNEL, text)
    except Exception as e:
        print(f"Failed to log message: {e}")

@app.on_message(filters.command("start"))
async def start_message(client: Client, message: Message):
    await message.reply_text(
        "👋 Hello! I can mass-report channels, groups, or bots using your session accounts.\n\n"
        "Use /report to start the process."
    )
    await log_to_channel(f"👋 Bot started by {message.from_user.mention} (ID: {message.from_user.id})")

# Step 1: Start report process
@app.on_message(filters.command("report"))
async def report_command(client: Client, message: Message):
    report_states[message.from_user.id] = {"step": "username"}
    await message.reply_text("🔎 Send the username or channel ID you want to report:")

# Step 2: Handle state machine
@app.on_message(filters.text & ~filters.command(["start", "report"]))
async def handle_report_steps(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in report_states:
        return

    state = report_states[user_id]

    # Step 1: Username / Channel ID
    if state["step"] == "username":
        state["target"] = message.text.strip()
        state["step"] = "count"
        await message.reply_text("📌 How many reports per session should I send?")
        return

    # Step 2: Count
    if state["step"] == "count":
        if not message.text.isdigit():
            await message.reply_text("❌ Please send a valid number.")
            return
        state["count"] = int(message.text)
        state["step"] = "reason"
        buttons = [
            [InlineKeyboardButton("🚫 Spam", callback_data="reason_spam")],
            [InlineKeyboardButton("👶 Child Abuse", callback_data="reason_child")],
            [InlineKeyboardButton("⚔️ Violence", callback_data="reason_violence")],
            [InlineKeyboardButton("🔞 Porn", callback_data="reason_porn")],
            [InlineKeyboardButton("📢 Copyright", callback_data="reason_copyright")],
            [InlineKeyboardButton("❓ Other", callback_data="reason_other")],
        ]
        await message.reply_text("⚠️ Choose report reason:", reply_markup=InlineKeyboardMarkup(buttons))
        return

    # Step 4: Description
    if state["step"] == "description":
        state["description"] = message.text.strip()
        await message.reply_text("🚀 Starting report process...")
        asyncio.create_task(start_reporting(user_id))
        del report_states[user_id]
        return

# Step 3: Reason selection
@app.on_callback_query(filters.regex(r"^reason_"))
async def handle_reason_callback(client: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in report_states:
        return
    reason = callback.data.replace("reason_", "")
    report_states[user_id]["reason"] = reason
    report_states[user_id]["step"] = "description"
    await callback.message.reply_text("✍️ Please provide a short description for the report.")
    await callback.answer()

# Function to map reason strings
def get_reason(reason: str):
    mapping = {
        "spam": types.InputReportReasonSpam(),
        "child": types.InputReportReasonChildAbuse(),
        "violence": types.InputReportReasonViolence(),
        "porn": types.InputReportReasonPornography(),
        "copyright": types.InputReportReasonCopyright(),
        "other": types.InputReportReasonOther(),
    }
    return mapping.get(reason, types.InputReportReasonSpam())

# Reporting function
async def report_channel(client, target, reason, description):
    try:
        if target.startswith("@"):
            chat = await client.get_chat(target)
            peer = await client.resolve_peer(chat.id)
        else:
            peer = await client.resolve_peer(int(target))

        result = await client.invoke(
            functions.account.ReportPeer(
                peer=peer,
                reason=get_reason(reason),
                message=description
            )
        )
        return True, str(result)
    except Exception as e:
        return False, str(e)

# Run reporting across all sessions
async def start_reporting(user_id):
    state = report_states.get(user_id, {})
    target = state["target"]
    count = state["count"]
    reason = state["reason"]
    description = state.get("description", "Reported by automation")

    await log_to_channel(f"🚀 Reporting started for {target}\nReason: {reason}\nDescription: {description}")

    for session_key, session_client in session_clients.items():
        for i in range(count):
            try:
                success, result = await report_channel(session_client, target, reason, description)
                if success:
                    await log_to_channel(f"✅ {session_key} reported {target} (reason={reason})")
                else:
                    await log_to_channel(f"❌ {session_key} failed: {result}")
                await asyncio.sleep(3)  # small delay to avoid FloodWait
            except Exception as e:
                await log_to_channel(f"❌ {session_key} error: {e}")

    await log_to_channel(f"🛑 Reporting finished for {target}")

# Start all session clients
for client in session_clients.values():
    client.start()

app.run()
