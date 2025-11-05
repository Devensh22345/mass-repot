from pyrogram import Client, filters, idle
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.raw import functions, types
from pyrogram.errors import FloodWait, PeerIdInvalid, UsernameInvalid, UsernameNotOccupied
import asyncio, random, time
from configs import cfg

# Bot client
app = Client("bot", api_id=cfg.API_ID, api_hash=cfg.API_HASH, bot_token=cfg.BOT_TOKEN)

# User sessions
session_clients = {}
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

# Store user data
user_data = {}

# ---------- Logging only in sudo DM ----------
async def log_to_user(user_id: int, text: str):
    try:
        await app.send_message(user_id, text)
    except Exception as e:
        print(f"Log DM failed: {e}")

# ---------- Start command ----------
@app.on_message(filters.command("start"))
async def start_message(client: Client, message: Message):
    if message.from_user.id not in cfg.SUDO:
        await message.reply_text("❌ Only sudo users can use this command.")
        return

    txt = (
        "👋 Hello! I can mass-report Telegram channels, groups, or bots.\n\n"
        "Commands:\n"
        "• /report → Start reporting flow\n"
        "• /stop → Cancel current reporting task\n\n"
        "⚠️ Only SUDO users can use this bot."
    )
    await message.reply_text(txt)
    await log_to_user(message.from_user.id, f"✅ Bot started by {message.from_user.mention} (ID: {message.from_user.id})")

# ---------- Report command ----------
@app.on_message(filters.command("report"))
async def report_command(client, message: Message):
    if message.from_user.id not in cfg.SUDO:
        await message.reply_text("❌ Only sudo users can use this command.")
        return

    user_data[message.from_user.id] = {"step": "username"}
    await message.reply_text("✍️ Send the username or ID of the target channel/group/bot (example: @badchannel):")

# ---------- Stop command ----------
@app.on_message(filters.command("stop"))
async def stop_command(client, message: Message):
    if message.from_user.id not in cfg.SUDO:
        await message.reply_text("❌ Only sudo users can use this command.")
        return

    if message.from_user.id in user_data:
        del user_data[message.from_user.id]
        await message.reply_text("✅ Operation cancelled.")
    else:
        await message.reply_text("❌ No active operation to cancel.")

# ---------- Handle messages ----------
@app.on_message(filters.text & filters.private)
async def handle_messages(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in cfg.SUDO:
        return
    
    if user_id not in user_data:
        return
    
    step = user_data[user_id].get("step")
    
    if step == "username":
        target = message.text.strip()
        if not (target.startswith('@') or target.lstrip('-').isdigit()):
            await message.reply_text("❌ Invalid username or ID. Please provide a valid username (starting with @) or numeric ID.")
            return
            
        user_data[user_id]["target"] = target
        user_data[user_id]["step"] = "count"
        await message.reply_text("🔢 How many reports to send from each session? (Max 10 recommended)")
        
    elif step == "count":
        try:
            count = int(message.text.strip())
            if count <= 0:
                await message.reply_text("❌ Number must be positive. Please enter a valid number.")
                return
            if count > 50:
                await message.reply_text("⚠️ That's a high number. Setting to maximum of 50.")
                count = 50
                
            user_data[user_id]["count"] = count
            user_data[user_id]["step"] = "reason"
            
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
            
    elif step == "description":
        if len(message.text.strip()) < 5:
            await message.reply_text("❌ Description too short. Please provide a more detailed description.")
            return
            
        user_data[user_id]["description"] = message.text.strip()
        await message.reply_text("🚀 Starting mass-reporting...")
        
        # Start reporting
        await start_reporting(user_id)
        
# ---------- Handle callback queries ----------
@app.on_callback_query(filters.regex(r"^reason_"))
async def handle_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in user_data:
        await callback_query.answer("❌ No active operation.", show_alert=True)
        return

    reason = callback_query.data.replace("reason_", "")
    user_data[user_id]["reason"] = reason
    user_data[user_id]["step"] = "description"
    await callback_query.message.edit_text("✍️ Send a short description for this report:")
    await callback_query.answer()

# ---------- Start reporting process ----------
async def start_reporting(user_id):
    if user_id not in user_data:
        await log_to_user(user_id, "❌ Report data not found.")
        return

    data = user_data[user_id]
    target = data["target"]
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
            # Try to join the chat first
            try:
                await sc.join_chat(target)
                await asyncio.sleep(random.uniform(2, 5))
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
                    await sc.invoke(functions.account.ReportPeer(
                        peer=peer,
                        reason=reason_obj,
                        message=description
                    ))
                    successful_reports += 1
                    if (i+1) % 5 == 0:
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
    if user_id in user_data:
        del user_data[user_id]
        
    await log_to_user(user_id, 
        f"🛑 Mass report completed for {target}\n"
        f"✅ Successful reports: {successful_reports}\n"
        f"❌ Failed sessions: {failed_sessions}"
    )

# ---------- Start all clients ----------
async def main():
    # Start session clients
    for session_key, client in session_clients.items():
        try:
            await client.start()
            print(f"✅ {session_key} started successfully")
        except Exception as e:
            print(f"❌ Failed to start {session_key}: {e}")
    
    # Start bot
    await app.start()
    print("Bot started!")
    
    # Get bot info
    me = await app.get_me()
    print(f"Bot: @{me.username} (ID: {me.id})")
    
    # Idle until stopped
    await idle()
    
    # Stop all clients
    for session_key, client in session_clients.items():
        try:
            await client.stop()
            print(f"✅ {session_key} stopped successfully")
        except Exception as e:
            print(f"❌ Failed to stop {session_key}: {e}")
    
    await app.stop()
    print("Bot stopped!")

# Run the bot
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Error: {e}")
