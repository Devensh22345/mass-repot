from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw import functions, types
import asyncio, random
from configs import cfg

# === Initialize Bot Client ===
app = Client(
    "bot",
    api_id=cfg.API_ID,
    api_hash=cfg.API_HASH,
    bot_token=cfg.BOT_TOKEN
)

# === Initialize Session Clients ===
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

# Start all session clients
for client in session_clients.values():
    client.start()

# === Config ===
LOG_CHANNEL = -1002820705251
report_state = {}

REPORT_REASONS = {
    "spam": types.InputReportReasonSpam(),
    "violence": types.InputReportReasonViolence(),
    "porn": types.InputReportReasonPornography(),
    "child": types.InputReportReasonChildAbuse(),
    "copyright": types.InputReportReasonCopyright(),
    "other": types.InputReportReasonOther()
}


async def log_to_channel(text: str):
    try:
        await app.send_message(LOG_CHANNEL, text)
    except Exception as e:
        print(f"Log failed: {e}")


# === Start Message ===
@app.on_message(filters.command("start"))
async def start_message(client: Client, message: Message):
    await message.reply_text(
        "👋 Hello!\n\n"
        "Commands:\n"
        "/report → Start reporting flow"
    )
    await log_to_channel(f"👋 Bot started by {message.from_user.mention} (ID: {message.from_user.id})")


# === Report Flow ===
@app.on_message(filters.command("report"))
async def report_command(client: Client, message: Message):
    user_id = message.from_user.id
    report_state[user_id] = {"step": "ask_target"}
    await message.reply_text("🔎 Send the @username or channel/group ID to report.")


@app.on_message(filters.text & ~filters.command(["start", "report"]))
async def handle_report_steps(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in report_state:
        return

    state = report_state[user_id]

    # Step 1: Target username/ID
    if state["step"] == "ask_target":
        state["target"] = message.text.strip()
        state["step"] = "ask_count"
        await message.reply_text("📊 How many reports per session account?")
        return

    # Step 2: Count
    if state["step"] == "ask_count":
        try:
            count = int(message.text.strip())
        except:
            await message.reply_text("❌ Please send a valid number.")
            return
        state["count"] = count
        state["step"] = "ask_reason"
        await message.reply_text(
            "⚠️ Choose report type:\n"
            "spam | violence | porn | child | copyright | other"
        )
        return

    # Step 3: Reason
    if state["step"] == "ask_reason":
        reason = message.text.lower().strip()
        if reason not in REPORT_REASONS:
            await message.reply_text("❌ Invalid reason. Choose from: spam, violence, porn, child, copyright, other")
            return
        state["reason"] = reason
        state["step"] = "ask_description"
        await message.reply_text("📝 Send report description (e.g., 'This channel spreads spam').")
        return

    # Step 4: Description
    if state["step"] == "ask_description":
        state["description"] = message.text.strip()
        await message.reply_text("✅ Starting reporting process...")
        await start_reporting(user_id)
        del report_state[user_id]


async def start_reporting(user_id: int):
    state = report_state[user_id]
    target = state["target"]
    count = state["count"]
    reason = REPORT_REASONS[state["reason"]]
    description = state["description"]

    for session_key, session_client in session_clients.items():
        try:
            # Resolve chat
            if target.startswith("@"):
                chat = await session_client.get_chat(target)
            else:
                chat = await session_client.get_chat(int(target))

            # Try to join (channels/groups only)
            try:
                await session_client.join_chat(chat.id)
                await log_to_channel(f"👤 {session_key} joined {target}")
            except Exception:
                pass

            peer = await session_client.resolve_peer(chat.id)

            for i in range(count):
                try:
                    await session_client.invoke(
                        functions.account.ReportPeer(
                            peer=peer,
                            reason=reason,
                            message=description
                        )
                    )
                    await log_to_channel(f"✅ {session_key} reported {target} ({state['reason']}) [{i+1}/{count}]")
                    await asyncio.sleep(random.randint(5, 15))  # delay to mimic real
                except Exception as e:
                    await log_to_channel(f"❌ {session_key} failed report {target}: {e}")
                    break

        except Exception as e:
            await log_to_channel(f"❌ {session_key} could not process {target}: {e}")

    await log_to_channel(f"🏁 Reporting finished for {target}")


# === Run Bot ===
app.run()
