from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.raw import functions, types
import asyncio, random
from configs import cfg

# Bot client
app = Client("bot", api_id=cfg.API_ID, api_hash=cfg.API_HASH, bot_token=cfg.BOT_TOKEN)

# User sessions
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

report_data = {}  # store per-user reporting state


# ---------- Logging only in sudo DM ----------
async def log_to_user(user_id: int, text: str):
    try:
        await app.send_message(user_id, text)
    except Exception as e:
        print(f"Log DM failed: {e}")


# ---------- Start command ----------
@app.on_message(filters.command("start"))
async def start_message(client: Client, message: Message):
    txt = (
        "👋 Hello! I can mass-report Telegram channels, groups, or bots.\n\n"
        "Commands:\n"
        "• /report → Start reporting flow\n"
        "• /stopreport → Cancel current reporting task\n\n"
        "⚠️ Only SUDO users can use this bot."
    )
    await message.reply_text(txt)
    await log_to_user(message.from_user.id, f"✅ Bot started by {message.from_user.mention} (ID: {message.from_user.id})")


# ---------- Step 1: /report ----------
@app.on_message(filters.command("report"))
async def report_command(client, message: Message):
    if message.from_user.id not in cfg.SUDO:
        await message.reply_text("❌ Only sudo users can use this command.")
        return

    report_data[message.from_user.id] = {}
    await message.reply_text("✍️ Send the username or ID of the target channel/group/bot (example: @badchannel):")
    report_data[message.from_user.id]["step"] = "username"


# ---------- Handle text replies in flow ----------
@app.on_message(filters.text & ~filters.command(["report", "start", "stopreport"]))
async def handle_text_reply(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in report_data or "step" not in report_data[user_id]:
        return

    step = report_data[user_id]["step"]

    # Step: username
    if step == "username":
        report_data[user_id]["username"] = message.text.strip()
        report_data[user_id]["step"] = "count"
        await message.reply_text("🔢 How many reports to send from each session?")
        return

    # Step: count
    if step == "count":
        try:
            count = int(message.text.strip())
            report_data[user_id]["count"] = count
            report_data[user_id]["step"] = "reason"
            buttons = [
                [InlineKeyboardButton("🚫 Spam", callback_data="reason_spam")],
                [InlineKeyboardButton("👶 Child Abuse", callback_data="reason_child")],
                [InlineKeyboardButton("🔪 Violence", callback_data="reason_violence")],
                [InlineKeyboardButton("🔞 Pornography", callback_data="reason_porn")],
                [InlineKeyboardButton("💿 Copyright", callback_data="reason_copyright")],
                [InlineKeyboardButton("❔ Other", callback_data="reason_other")]
            ]
            await message.reply_text("⚠️ Select report reason:", reply_markup=InlineKeyboardMarkup(buttons))
        except:
            await message.reply_text("❌ Invalid number. Send an integer.")
        return

    # Step: description
    if step == "description":
        report_data[user_id]["description"] = message.text.strip()
        await message.reply_text("🚀 Starting mass-reporting...")
        await start_reporting(user_id, message)
        report_data.pop(user_id, None)


# ---------- Handle reason selection ----------
@app.on_callback_query(filters.regex(r"^reason_"))
async def handle_reason_callback(client: Client, cq: CallbackQuery):
    user_id = cq.from_user.id
    if user_id not in report_data:
        await cq.answer("❌ No active report.", show_alert=True)
        return

    reason = cq.data.replace("reason_", "")
    report_data[user_id]["reason"] = reason
    report_data[user_id]["step"] = "description"
    await cq.message.reply_text("✍️ Send a short description for this report:")


# ---------- Start reporting process ----------
async def start_reporting(user_id, message: Message):
    data = report_data[user_id]
    target = data["username"]
    reason = data["reason"]
    count = data["count"]
    description = data["description"]

    reason_map = {
        "spam": types.InputReportReasonSpam(),
        "child": types.InputReportReasonChildAbuse(),
        "violence": types.InputReportReasonViolence(),
        "porn": types.InputReportReasonPornography(),
        "copyright": types.InputReportReasonCopyright(),
        "other": types.InputReportReasonOther()
    }
    reason_obj = reason_map.get(reason, types.InputReportReasonSpam())

    await log_to_user(user_id,
        f"🚨 Mass report started\n"
        f"Target: {target}\nReason: {reason}\nReports per session: {count}"
    )

    for session_key, sc in session_clients.items():
        try:
            await sc.join_chat(target)  # join channel/group first
        except Exception as e:
            await log_to_user(user_id, f"⚠️ {session_key} failed to join {target}: {e}")

        try:
            chat = await sc.get_chat(target)
            peer = await sc.resolve_peer(chat.id)
        except Exception as e:
            await log_to_user(user_id, f"❌ {session_key} failed to resolve {target}: {e}")
            continue

        for i in range(count):
            try:
                await sc.invoke(functions.account.ReportPeer(
                    peer=peer,
                    reason=reason_obj,
                    message=description
                ))
                await log_to_user(user_id, f"✅ {session_key} → Report {i+1}/{count} sent for {target}")
                await asyncio.sleep(random.randint(5, 15))  # small delay
            except Exception as e:
                await log_to_user(user_id, f"❌ {session_key} report failed: {e}")
                await asyncio.sleep(3)

    await log_to_user(user_id, f"🛑 Mass report completed for {target}")


# ---------- Start all session clients ----------
for client in session_clients.values():
    client.start()

app.run()
