from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.raw import functions, types
from pyrogram.errors import FloodWait, PeerIdInvalid, UsernameInvalid, UsernameNotOccupied
import asyncio, random, time
from configs import cfg

# Bot client
app = Client("bot", api_id=cfg.API_ID, api_hash=cfg.API_HASH, bot_token=cfg.BOT_TOKEN)

# User sessions with improved error handling
session_clients = {}
active_reports = {}  # Track active reporting tasks for cancellation

for i in range(1, 31):
    session_key = f"session{i}"
    session_string = getattr(cfg, f"SESSION_STRING_{i}", None)
    if session_string and session_string.strip():
        try:
            session_clients[session_key] = Client(
                session_key,
                api_id=cfg.API_ID,
                api_hash=cfg.API_HASH,
                session_string=session_string
            )
        except Exception as e:
            print(f"Failed to initialize {session_key}: {e}")

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

    # Check if user already has an active report
    if message.from_user.id in active_reports:
        await message.reply_text("❌ You already have an active reporting task. Use /stopreport to cancel it first.")
        return

    report_data[message.from_user.id] = {}
    await message.reply_text("✍️ Send the username or ID of the target channel/group/bot (example: @badchannel):")
    report_data[message.from_user.id]["step"] = "username"

# ---------- Stop report command ----------
@app.on_message(filters.command("stopreport"))
async def stop_report_command(client, message: Message):
    user_id = message.from_user.id
    if user_id not in active_reports:
        await message.reply_text("❌ You don't have any active reporting tasks.")
        return
    
    # Cancel the reporting task
    active_reports[user_id].cancel()
    del active_reports[user_id]
    
    # Clean up report data
    if user_id in report_data:
        del report_data[user_id]
    
    await message.reply_text("✅ Reporting task cancelled.")
    await log_to_user(user_id, "🛑 Reporting task cancelled by user.")

# ---------- Handle text replies in flow ----------
@app.on_message(filters.text & ~filters.command(["report", "start", "stopreport"]))
async def handle_text_reply(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in report_data or "step" not in report_data[user_id]:
        return

    step = report_data[user_id]["step"]

    # Step: username
    if step == "username":
        target = message.text.strip()
        # Basic validation
        if not (target.startswith('@') or target.lstrip('-').isdigit()):
            await message.reply_text("❌ Invalid username or ID. Please provide a valid username (starting with @) or numeric ID.")
            return
            
        report_data[user_id]["username"] = target
        report_data[user_id]["step"] = "count"
        await message.reply_text("🔢 How many reports to send from each session? (Max 10 recommended)")
        return

    # Step: count
    if step == "count":
        try:
            count = int(message.text.strip())
            if count <= 0:
                await message.reply_text("❌ Number must be positive. Please enter a valid number.")
                return
            if count > 50:  # Reasonable limit
                await message.reply_text("⚠️ That's a high number. Setting to maximum of 50.")
                count = 50
                
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
        except ValueError:
            await message.reply_text("❌ Invalid number. Please send a valid integer.")
        return

    # Step: description
    if step == "description":
        if len(message.text.strip()) < 5:
            await message.reply_text("❌ Description too short. Please provide a more detailed description.")
            return
            
        report_data[user_id]["description"] = message.text.strip()
        await message.reply_text("🚀 Starting mass-reporting...")
        
        # Create a task for reporting to avoid blocking
        task = asyncio.create_task(start_reporting(user_id, message))
        active_reports[user_id] = task
        return

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
    await cq.message.edit_text("✍️ Send a short description for this report:")
    await cq.answer()

# ---------- Start reporting process ----------
async def start_reporting(user_id, message: Message):
    data = report_data.get(user_id)
    if not data:
        await log_to_user(user_id, "❌ Report data not found.")
        return

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

    successful_reports = 0
    failed_sessions = 0
    
    for session_key, sc in session_clients.items():
        try:
            # Check if task was cancelled
            if user_id not in active_reports:
                break
                
            # Try to join the chat first
            try:
                await sc.join_chat(target)
                await asyncio.sleep(random.uniform(2, 5))  # Random delay
            except (PeerIdInvalid, UsernameInvalid, UsernameNotOccupied):
                await log_to_user(user_id, f"❌ {session_key}: Invalid target {target}")
                failed_sessions += 1
                continue
            except FloodWait as e:
                await log_to_user(user_id, f"⏳ {session_key}: Flood wait for {e.value} seconds")
                await asyncio.sleep(e.value + 2)
                continue
            except Exception as e:
                await log_to_user(user_id, f"⚠️ {session_key}: Failed to join {target}: {e}")
                failed_sessions += 1
                continue

            # Resolve the chat
            try:
                chat = await sc.get_chat(target)
                peer = await sc.resolve_peer(chat.id)
            except Exception as e:
                await log_to_user(user_id, f"❌ {session_key}: Failed to resolve {target}: {e}")
                failed_sessions += 1
                continue

            # Send reports
            for i in range(count):
                try:
                    # Check if task was cancelled
                    if user_id not in active_reports:
                        break
                        
                    await sc.invoke(functions.account.ReportPeer(
                        peer=peer,
                        reason=reason_obj,
                        message=description
                    ))
                    successful_reports += 1
                    if (i+1) % 5 == 0:  # Log progress every 5 reports
                        await log_to_user(user_id, f"✅ {session_key} → {i+1}/{count} reports sent for {target}")
                    
                    # Random delay between reports
                    await asyncio.sleep(random.uniform(10, 30))
                    
                except FloodWait as e:
                    await log_to_user(user_id, f"⏳ {session_key}: Flood wait for {e.value} seconds")
                    await asyncio.sleep(e.value + 2)
                except Exception as e:
                    await log_to_user(user_id, f"❌ {session_key}: Report failed: {e}")
                    await asyncio.sleep(5)

        except Exception as e:
            await log_to_user(user_id, f"❌ {session_key}: Unexpected error: {e}")
            failed_sessions += 1

    # Clean up
    if user_id in active_reports:
        del active_reports[user_id]
    if user_id in report_data:
        del report_data[user_id]
        
    await log_to_user(user_id, 
        f"🛑 Mass report completed for {target}\n"
        f"✅ Successful reports: {successful_reports}\n"
        f"❌ Failed sessions: {failed_sessions}"
    )

# ---------- Start all session clients ----------
async def start_clients():
    for session_key, client in session_clients.items():
        try:
            await client.start()
            print(f"✅ {session_key} started successfully")
        except Exception as e:
            print(f"❌ Failed to start {session_key}: {e}")

# ---------- Stop all session clients ----------
async def stop_clients():
    for session_key, client in session_clients.items():
        try:
            await client.stop()
            print(f"✅ {session_key} stopped successfully")
        except Exception as e:
            print(f"❌ Failed to stop {session_key}: {e}")

# ---------- Main function ----------
async def main():
    await start_clients()
    await app.start()
    print("Bot started!")
    
    # Get bot info
    me = await app.get_me()
    print(f"Bot: @{me.username} (ID: {me.id})")
    
    # Run until stopped
    await asyncio.Event().wait()

# Run with proper cleanup
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        asyncio.run(stop_clients())
        print("All clients stopped.")
